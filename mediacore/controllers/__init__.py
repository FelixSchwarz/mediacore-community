def check_user_autentication(request):
    # devo controllare se l'utente e' autenticato o meno
    if hasattr(request, 'identity'):
        userid = request.identity['repoze.who.userid']
    else:
        request.identity = request.environ.get('repoze.who.identity')
        if request.identity:
            # current user is authenticated
            userid = request.identity['repoze.who.userid']
        else:
            # current user is anonymous
            userid = None

    return userid