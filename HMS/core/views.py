from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.google_auth import get_flow
import json


@login_required
def google_oauth_start(request):
    flow = get_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    request.session['oauth_state'] = state
    return redirect(authorization_url)


@login_required
def google_oauth_callback(request):
    state = request.session.get('oauth_state')
    flow = get_flow()
    flow.fetch_token(authorization_response=request.build_absolute_uri())

    credentials = flow.credentials
    token_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'scopes': list(credentials.scopes) if credentials.scopes else [],
    }
    request.user.google_token = token_data
    request.user.save()

    messages.success(request, '✅ Google Calendar connected successfully!')
    return redirect('dashboard')
