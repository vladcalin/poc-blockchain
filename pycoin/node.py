import click
import flask

from pycoin.blockchain import Blockchain
from pycoin.consts import Network
from pycoin.exceptions import PyCoinException

app = flask.Flask(__name__)
blockchain = Blockchain()


@app.route('/blockchain/block_count')
def block_count():
    return flask.jsonify({
        'block_count': blockchain.get_block_count()
    })


@app.route('/blockchain/blocks')
def filter_blocks():
    start_index = flask.request.args.get('start')
    end_index = flask.request.args.get('end')
    verbose = flask.request.args.get('verbose', False)
    return flask.jsonify(
        blockchain.get_blocks(start_index, end_index, verbose=verbose))


@app.route('/tx/submit', methods=['post'])
def submit_transaction():
    post_data = flask.request.form
    from_addr = post_data.get('from')
    to_addr = post_data.get('to')
    amount = float(post_data.get('amount'))
    signature = post_data.get('signature')
    public_key = post_data.get('public_key')
    ts = float(post_data.get('ts'))
    try:
        blockchain.submit_transaction(from_addr, to_addr, amount, ts, signature,
                                      public_key)
    except PyCoinException as err:
        return flask.Response(repr(err), status=400)
    return 'Submitted'


@app.route('/wallets/info/<address>')
def wallet_info(address):
    return flask.jsonify(blockchain.get_address_info(address))


@click.group()
def cli():
    pass


@cli.command('start')
def start_node():
    app.run('0.0.0.0', Network.NODE_PORT, debug=True)


if __name__ == '__main__':
    cli()
