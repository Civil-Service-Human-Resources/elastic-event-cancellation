import requests
import mysql.connector
import os


ELASTIC_REPO_ENDPOINT = os.environ['ELASTIC_REPO_ENDPOINT']
ELASTIC_REPO_USERNAME = os.environ['ELASTIC_REPO_USERNAME']
ELASTIC_REPO_PASSWORD = os.environ['ELASTIC_REPO_PASSWORD']

MYSQL_HOST = os.environ['MYSQL_HOST']
MYSQL_USER = os.environ['MYSQL_USER']
MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD']


def get_mysql_connection():
    return mysql.connector.connect(
        database='learner_record',
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD
    )


def get_cancelled_events():
    conn = get_mysql_connection()
    with conn.cursor() as cursor:
        sql = """
            select e.uid, e.cancellation_reason
            from learner_record.event e
            where e.status = 'CANCELLED'
        """
        cursor.execute(sql)
        return [(row[0], row[1]) for row in cursor.fetchall()]


class ElasticClient():

    def __init__(self, elastic_url, elastic_username, elastic_pw) -> None:
        self.elastic_url = elastic_url
        self.elastic_username = elastic_username
        self.elastic_pw = elastic_pw

    def _get_auth(self):
        return (self.elastic_username, self.elastic_pw)

    def search_for_event(self, event_id):
        response = requests.post(
            f"{self.elastic_url}/courses/_search",
            json={
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "modules.events.id": event_id
                                }
                            }
                        ]
                    }
                }
            },
            auth=self._get_auth()
        )
        data = response.json()
        return {
            "total": data['hits']['total'],
            "content": data['hits']['hits']
        }

    def update_course(self, course):
        response = requests.put(
            f"{self.elastic_url}/courses/_doc/" + course['id'],
            json=course,
            auth=self._get_auth()
        )
        if response.status_code >= 400:
            print(f"Error updating: {response.text}")

    def cancel_event(self, event_id, reason, commit=True):
        course_resp = self.search_for_event(event_id)['content']
        if len(course_resp) > 0:
            course = course_resp[0]['_source']
            for _module in course.get('modules', []):
                for event in _module.get('events', []):
                    if event['id'] == event_id:
                        event_status = event.get('status', None)
                        event_cancellation_reason = event.get('cancellationReason', None)
                        print(f"Found event with id '{event_id}'. Status: '{event_status}'. Cancellation reason: '{event_cancellation_reason}'")
                        if event_status != 'Cancelled':
                            event['status'] = 'Cancelled'
                        if event_cancellation_reason is None:
                            event['cancellationReason'] = reason
                        if commit:
                            self.update_course(course)
                            print(f"Updated event '{event_id}' to 'Cancelled' status with reason '{reason}'")
                        else:
                            print("Did not commit")
                        return
        else:
            print(f"No course found for event ID '{event_id}'")


client = ElasticClient(ELASTIC_REPO_ENDPOINT, ELASTIC_REPO_USERNAME, ELASTIC_REPO_PASSWORD)

cancelled_ids = get_cancelled_events()
print(f"Found {len(cancelled_ids)} cancelled events")
for _id, reason in cancelled_ids:
    if _id and reason:
        client.cancel_event(_id, reason, False)
