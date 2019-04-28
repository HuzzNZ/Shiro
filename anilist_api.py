import requests
import asyncio


async def find_anime_by_name(anime_name):
    query = """
        query ($search: String) {
          Media(search: $search, type: ANIME) {
            id

            title {
              romaji
              english
              native
            }

            description

            meanScore

            averageScore

            popularity

            episodes

            status

            duration

            seasonInt

            genres

            studios(isMain:true) {
              edges {
                node {
                  name
                }
              }
            }

            format

            airingSchedule(notYetAired:true, page:1, perPage:1) {
              edges {
                node{
                  episode
                  airingAt
                  timeUntilAiring
                }
              }
            }

            siteUrl

            coverImage {
                extraLarge
              color
            }
          }
        }
        """
    url = "https://graphql.anilist.co"

    variables = f"""
        {{
            "search": "{anime_name}"
        }}
        """
    response = requests.post(url, json={'query': query, 'variables': variables})
    data = response.json()["data"]["Media"]
    return data


async def find_anime_by_id(anime_id):
    query = """
    query ($id: Int) {
      Media(id: $id, type: ANIME) {
        id

        title {
          romaji
          english
          native
        }

        description

        meanScore

        averageScore

        popularity

        episodes

        status

        duration

        seasonInt

        genres

        studios(isMain:true) {
          edges {
            node {
              name
            }
          }
        }

        format

        airingSchedule(notYetAired:true, page:1, perPage:1) {
          edges {
            node{
              episode
              airingAt
              timeUntilAiring
            }
          }
        }

        siteUrl

        coverImage {
            extraLarge
          color
        }
      }
    }
    """
    url = "https://graphql.anilist.co"

    variables = f"""
    {{
        "id": {anime_id}
    }}
    """
    response = requests.post(url, json={'query': query, 'variables': variables})
    data = response.json()["data"]["Media"]
    return data


async def find_manga_by_id(manga_id):
    query = '''
    query ($id: Int) {
      Media(id: $id, type: MANGA) {
        id
        title {
          romaji
          english
          native
        }
        description
        startDate {
          year
          month
          day
        }
        meanScore
        status
        genres
        staff {
          nodes {
            name {
              first
              last
            }
          }
        }
        format
        siteUrl
        coverImage {
          extraLarge
          color
        }
      }
    }
    '''
    url = "https://graphql.anilist.co"
    variables = f"""
    {{
        "id": {manga_id}
    }}
    """
    response = requests.post(url, json={'query': query, 'variables': variables})
    data = response.json()["data"]["Media"]
    return data


async def find_manga_by_name(manga_name):
    query = '''
    query ($search: String) {
      Media(search: $search, type: MANGA) {
        id
        title {
          romaji
          english
          native
        }
        description
        startDate {
          year
          month
          day
        }
        meanScore
        status
        genres
        staff {
          nodes {
            name {
              first
              last
            }
          }
        }
        format
        siteUrl
        coverImage {
          extraLarge
          color
        }
      }
    }
    '''
    url = "https://graphql.anilist.co"
    variables = f"""
    {{
        "search": "{manga_name}"
    }}
    """
    response = requests.post(url, json={'query': query, 'variables': variables})
    data = response.json()["data"]["Media"]
    return data


if __name__ == "__main__":
    print(asyncio.get_event_loop().run_until_complete(find_anime_by_id(101921)))
