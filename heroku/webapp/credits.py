### credit transactions
## If you touch this shit without telling me I will fuck you up

## EXCHANGE is a magic user who we can give funds to via backdoor.
## Adding/removing funds to a user account directly (as in, not user-to-user)
## is done by making transactions to/from EXCHANGE.
## This is NOT a scalable solution because EXCHANGE's user profile is locked
## for every transaction.

## Assumes credits never overflow.

from django.db import transaction
from django.contrib.auth.models import User
from webapp import models
from django.views.decorators.csrf import csrf_exempt
from webapp.helpers import JsonResponse

def record_transaction(from_username, to_username, amount, timestamp, bid=None):
    """ Just records the transaction. Assumes caller is handling correctness / locking. """
    #TODO logger thing
    trans = models.Transaction(
        from_user = User.objects.get(username=from_username),
        to_user = User.objects.get(username=to_username),
        amount = amount,
        time = timestamp,
        bid = bid
    )
    trans.save()
    

@transaction.commit_on_success
def try_transact_funds(from_username, to_username, amount, bid=None):
    """ Returns (success, msg) tuple """
    try:
        from_prof = User.objects.get(username=from_username).profile
        to_prof = User.objects.get(username=to_username).profile
    except User.DoesNotExist:
        print "uh oh"
        #TODO logger

    try:
        _lock_dat_shit(from_prof, 'credits')
        _lock_dat_shit(to_prof, 'credits')
        if (from_prof.credits < amount):
            if from_username == 'EXCHANGE': # if the exchange runs out, re-up it
                from_prof.credits += 10000 + amount # in case transaction is more than 10000
            else:
                return (False, "Not enough credits") 

        #TODO think of more ways this could go wrong
        
        record_transaction(from_username, to_username, amount, datetime.now(), bid)
        from_prof.credits -= amount
        to_prof.credits += amount
        # saves in finally block
        return (True, "success")

    except Exception, msg:
        return (False, "Something went wrong")
        #TODO log(msg)

    finally:
        # unlocks the fields
        from_prof.save()
        to_prof.save()


@transaction.commit_on_success
def add_credit_backdoor(username, amount):
    """ Use try_transact_credits to make all transactions except backdoor bonuses """
    user = User.objects.get(username=username)
    user_profile = user.profile
    _lock_dat_shit(user_profile, 'credits')
    try:
        # safety zone start
        user_profile.credits += amount
        record_transaction('EXCHANGE', username, amount, datetime.now(), None)
    finally:
        user_profile.save()
        # safety zone end


@csrf_exempt
def credit_test(request):
    res = ''

    if (request.GET.get('act') == 'transact'):
        success, msg = try_transact_funds('nikolai', 'u1', 5)
        res += msg
    elif request.GET.get('act') == 'add':
        add_credit_backdoor(request.GET.get('username'), int(request.GET.get('amount')))
        res += 'added credits'

    return JsonResponse(res)

