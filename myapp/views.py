from django.shortcuts import render
from django.conf import settings
from .models import Transaction
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt

def initiate_payment(request):
    try:
        amount = int(request.POST['amount'])
    except:
        return render(request, 'pay.html', context={'error': 'Invalid account details or amount'})

    try:
        transaction = Transaction.objects.create(amount=amount)
        transaction.save()
        merchant_key = settings.PAYTM_SECRET_KEY

        params = (
            ('MID', "hCcAFy87251810950007"),
            ('ORDER_ID', str(transaction.order_id)),
            ('CUST_ID', "shubhamgor752@gmail.com"),
            ('TXN_AMOUNT', str(transaction.amount)),
            ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
            ('WEBSITE', settings.PAYTM_WEBSITE),
            ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
            ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
        )

        print("MID: ", settings.PAYTM_MERCHANT_ID)
        print("ORDER_ID: ", str(transaction.order_id))
        print("CUST_ID: ", "shubhamgor752@gmail.com")
        print("TXN_AMOUNT: ", str(transaction.amount))
        print("CHANNEL_ID: ", settings.PAYTM_CHANNEL_ID)
        print("WEBSITE: ", settings.PAYTM_WEBSITE)
        print("INDUSTRY_TYPE_ID: ", settings.PAYTM_INDUSTRY_TYPE_ID)

        paytm_params = dict(params)
        checksum = generate_checksum(paytm_params, merchant_key)

        transaction.checksum = checksum
        transaction.save()

        paytm_params['CHECKSUMHASH'] = checksum
        print('Checksum sent: ', checksum)
        return render(request, 'redirect.html', context=paytm_params)

    except Exception as e:
        print(e)
        return render(request, 'pay.html', context={'error': 'Error initiating payment'})

@csrf_exempt
def callback(request):
    try:
        if request.method == 'POST':
            received_data = dict(request.POST)
            paytm_params = {}
            paytm_checksum = received_data['CHECKSUMHASH'][0]

            for key, value in received_data.items():
                if key == 'CHECKSUMHASH':
                    paytm_checksum = value[0]
                else:
                    paytm_params[key] = str(value[0])

            is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, paytm_checksum)
            received_data['message'] = "Checksum Matched" if is_valid_checksum else "Checksum Mismatched"

            # Additional logic for payment confirmation can be added here
            return render(request, 'callback.html', context=received_data)

    except Exception as e:
        print(e)
        return render(request, 'callback.html', context={'error': 'Error processing callback'})