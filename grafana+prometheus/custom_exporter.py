from prometheus_client import start_http_server, Gauge, Info
import requests, time, os, traceback, isodate

API_KEY = "AIzaSyBGh65pb-jiy5sUqrj9l3cUpbU-hWX_rVo"
CHANNEL_ID = os.getenv("YT_CHANNEL_ID", "UCDPk9MG2RexnOMGTD-YnSnA") 

if not API_KEY:
    raise SystemExit("Missing YT_API_KEY environment variable")

youtube_subscribers = Gauge('youtube_subscribers', 'Subscribers count')
youtube_views = Gauge('youtube_total_views', 'Total channel views')
youtube_videos = Gauge('youtube_video_count', 'Total uploaded videos')
youtube_latest_views = Gauge('youtube_latest_video_views', 'Views of latest video')
youtube_latest_likes = Gauge('youtube_latest_video_likes', 'Likes of latest video')
youtube_latest_comments = Gauge('youtube_latest_video_comments', 'Comments of latest video')
youtube_api_status = Gauge('youtube_api_status', 'API status 1=OK,0=DOWN')
youtube_latest_duration = Gauge('youtube_latest_video_duration_seconds', 'Duration of latest video')
youtube_channel_title = Info('youtube_channel_title', 'Channel title')
youtube_update_time = Gauge('youtube_update_timestamp', 'Last update timestamp')

def fetch_youtube_data():
    try:
        stats_url = "https://www.googleapis.com/youtube/v3/channels"
        stats_params = {'id': CHANNEL_ID, 'part': 'statistics,snippet', 'key': API_KEY}
        stats = requests.get(stats_url, params=stats_params).json()
        data = stats['items'][0]
        title = data['snippet']['title']
        subscribers = int(data['statistics']['subscriberCount'])
        views = int(data['statistics']['viewCount'])
        videos = int(data['statistics']['videoCount'])

        youtube_subscribers.set(subscribers)
        youtube_views.set(views)
        youtube_videos.set(videos)
        youtube_channel_title.info({'title': title})

        uploads_url = "https://www.googleapis.com/youtube/v3/search"
        uploads_params = {'channelId': CHANNEL_ID, 'order': 'date', 'maxResults': 1, 'part': 'id', 'type': 'video', 'key': API_KEY}
        uploads = requests.get(uploads_url, params=uploads_params).json()
        latest_video_id = uploads['items'][0]['id']['videoId']

        video_url = "https://www.googleapis.com/youtube/v3/videos"
        video_params = {'id': latest_video_id, 'part': 'statistics,contentDetails', 'key': API_KEY}
        video_data = requests.get(video_url, params=video_params).json()
        video_stats = video_data['items'][0]['statistics']
        video_details = video_data['items'][0]['contentDetails']

        youtube_latest_views.set(int(video_stats['viewCount']))
        youtube_latest_likes.set(int(video_stats.get('likeCount', 0)))
        youtube_latest_comments.set(int(video_stats.get('commentCount', 0)))
        duration_seconds = int(isodate.parse_duration(video_details['duration']).total_seconds())
        youtube_latest_duration.set(duration_seconds)

        youtube_api_status.set(1)
        youtube_update_time.set(time.time())
        print(f" Updated metrics for {title}")

    except Exception as e:
        youtube_api_status.set(0)
        print(" Error fetching YouTube data:", e)
        traceback.print_exc()

if __name__ == "__main__":
    print("YouTube Exporter running at http://localhost:8000/metrics")
    start_http_server(8000)
    while True:
        fetch_youtube_data()
        time.sleep(20)
