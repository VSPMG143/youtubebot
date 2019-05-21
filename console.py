from pytube import YouTube

from client import get_stream


def main():
    while True:
        url = input('Input video url: ')
        try:
            yt = YouTube(url)
            stream = get_stream(yt)
            stream.download('/home/neri/downloads')
            print('Success download!', yt.title)
        except Exception as e:
            print(e, url)


if __name__ == '__main__':
    main()
