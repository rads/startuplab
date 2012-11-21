from functools import wraps
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
import json

def JsonResponse(obj):
    return HttpResponse(json.dumps(obj), mimetype="application/json")

def render_to(template, mimetype=None):
    """ Use this decorator to render the returned dictionary from a function
        to a template in the proper context. If return value is not a dictionary,
        it is not modified. """
    def renderer(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            output = func(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output
            return render_to_response(template, 
                                      output, 
                                      context_instance=RequestContext(request),
                                      mimetype=mimetype)
        return wrapper
    return renderer

def simplify(bid):
    ret = {}
    ret['id'] = bid.id
    ret['title'] = bid.title
    ret['description'] = bid.description
    ret['expiretime'] = str(bid.expiretime)
    ret['posttime'] = str(bid.posttime)
    ret['amount'] = bid.initialOffer
    tags = []
    for tag in bid.tags.all():
        tags.append(tag.name)
    ret['tags'] = tags
    return ret

def _sql_lock_string(sql):
    return sql + ' FOR UPDATE' 

def _lock_dat_shit(model_instance, field):
    """ 
        Given a model instance and a field name (string), calling this function
        will lock the row corresponding to the model instance until an UPDATE is
        called on that row, and then update that field on the model instance with
        the locked value in the DB. 
        YOU MUST CALL THIS FUNCTION FROM SOMETHING WRAPPED IN @transaction.commit_on_success
        WHICH ALSO CALLS model_instance.save() OR ELSE I CAN'T GUARANTEE WTF WILL HAPPEN
        This means you MUST wrap this in a try block where you release the lock in 
        "finally" in case shit goes wrong.
    """
    #TODO make this into something I can use in a 'with' block

    model_type = model_instance.__class__
    query = model_type.objects.filter(id = model_instance.id).values_list(field)
    
    # get the SQL that django would have generated
    (raw_sql, params) = query._as_sql(connection=connection)
    sql = ''

    # don't do anything locally because SQLite sucks
    # TODO(nikolai) set up postgres on dev machine so that we don't have to deploy to test
    if settings.DEBUG:
        sql = raw_sql
    else:
        sql = _sql_lock_string(raw_sql)

    # LOCK DAT SHIT
    cursor = connection.cursor()
    cursor.execute(sql, params)
    
    # MAKE SURE NOBODY FUCKS WITH OUR FIELD, YO
    field_value = cursor.fetchone()[0]
    setattr(model_instance, field, field_value)

