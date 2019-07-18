import click

from .client import Client


@click.group()
@click.option('--token', required=True, envvar='API_TOKEN')
@click.option('--url', 'base_url',
              default='https://dev.api.anymotion.jp/api/v1/',
              envvar='API_URL')
@click.pass_context
def cli(ctx, token, base_url):
    ctx.ensure_object(dict)
    ctx.obj['client'] = Client(token, base_url)


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.pass_context
def upload(ctx, path):
    c = ctx.obj['client']
    media_id, media_type = c.upload_to_s3(path)
    click.echo(
        f'uploaded the {media_type} file to s3 ({media_type}_id: {media_id})')


@cli.group()
def movie():
    pass


@movie.command()
@click.pass_context
def list(ctx):
    c = ctx.obj['client']
    c.show_list('movies')


@cli.group()
def image():
    pass


@image.command()
@click.pass_context
def list(ctx):
    c = ctx.obj['client']
    c.show_list('images')


@cli.group()
def keypoint():
    pass


@keypoint.command()
@click.pass_context
def list(ctx):
    c = ctx.obj['client']
    c.show_list('keypoints')


@keypoint.command()
@click.option('--movie_id', type=int)
@click.option('--image_id', type=int)
@click.pass_context
def extract(ctx, movie_id, image_id):
    if movie_id is None and image_id is None:
        click.echo(
            'Error Missing option: Either "movie_id" or "image_id" is required.'
        )
        return

    c = ctx.obj['client']
    c.extract_keypoint(movie_id=movie_id, image_id=image_id)


@keypoint.command()
@click.argument('keypoint_id', type=int)
@click.pass_context
def show(ctx, keypoint_id):
    c = ctx.obj['client']
    keypoint = c.get_keypoint(keypoint_id)
    click.echo(keypoint)


@cli.command()
@click.argument('keypoint_id', type=int)
@click.option('--rule_id', default=0, type=int)
@click.option('-o', '--out_dir', default='.', type=click.Path())
@click.pass_context
def drawing(ctx, keypoint_id, rule_id, out_dir):
    c = ctx.obj['client']
    url = c.draw_keypoint(keypoint_id, rule_id)

    if url is not None:
        c.download(url, out_dir)


@cli.command()
@click.argument('keypoint_id', type=int)
@click.option('--rule_id', required=True, type=int)
@click.option('--show_result', is_flag=True)
@click.pass_context
def analysis(ctx, keypoint_id, rule_id, show_result):
    c = ctx.obj['client']
    result = c.analyze_keypoint(keypoint_id, rule_id)
    if show_result:
        click.echo(result)


def main():
    cli()


if __name__ == "__main__":
    main()
