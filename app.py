import os
from flask import Flask, redirect, abort
from sqlalchemy import select
from database.db import async_session, Link

app = Flask(__name__)


async def get_redirect_url(request: str) -> str:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(Link).filter(Link.request == request))
            link = result.scalars().first()
            if link:
                return link.redirect_url
            return None


@app.route('/<request>')
async def redirect_to_url(request: str):
    redirect_url = await get_redirect_url(request)
    if redirect_url:
        return redirect(redirect_url, code=302)
    else:
        return abort(404)


@app.route('/')
def hello():
    return redirect('https://poshmark.com/', code=302)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
