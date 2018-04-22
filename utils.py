def get_stream(yt):
    streams = yt.streams.filter(file_extension='mp4', only_video=True). \
        order_by('resolution').desc().all()
    for stream in streams:
        if stream.resolution <= '720p':
            return stream
