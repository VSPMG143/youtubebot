def get_stream(yt):
    streams = yt.streams.filter(file_extension='mp4', type='video').order_by('resolution').desc().all()
    for stream in streams:
        if stream.includes_audio_track and stream.resolution <= '720p':
            return stream
    return yt.streams.first()
