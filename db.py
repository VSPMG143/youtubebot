import sqlalchemy as sa


metadata = sa.MetaData()

videos = sa.Table(
    'videos', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(255)),
    sa.Column('url', sa.String(255)),
    sa.Column('download', sa.Boolean, default=False),
)

