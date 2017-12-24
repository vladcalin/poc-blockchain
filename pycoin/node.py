import click
import flask

from pycoin.blockchain import Blockchain
from pycoin.consts import Network

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
    return flask.jsonify(blockchain.get_blocks(start_index, end_index))


@app.route('/tx/submit', methods=['post'])
def submit_transaction():
    post_data = flask.request.form
    from_addr = post_data.get('from')
    to_addr = post_data.get('to')
    amount = float(post_data.get('amount'))
    signature = post_data.get('signature')
    public_key = post_data.get('public_key')
    ts = float(post_data.get('ts'))
    blockchain.submit_transaction(from_addr, to_addr, amount, ts, signature,
                                  public_key)
    return 'Submitted'


@click.group()
def cli():
    pass


@cli.command('start')
def start_node():
    app.run('0.0.0.0', Network.NODE_PORT, debug=True)


if __name__ == '__main__':
    cli()
