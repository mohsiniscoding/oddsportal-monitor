import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep
from telegram_bot import send_message
import random

driver = uc.Chrome()
driver.maximize_window()

driver.get('https://www.oddsportal.com/community/feed')
input("After logging in, press ENTER to continue:")

def get_most_recent_post_time():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    outer_div = soup.find('div', {'class': 'flex w-full flex-col text-xs'})
    inner_div = outer_div.find('div', {'class': 'owner-data flex w-full items-start gap-3 pt-2'})

    post_time_p = inner_div.find('p', {'class': 'text-gray-dark text-[12px] font-normal leading-[16px]'})
    convert_to_datetime = post_time_p.text.split(', ')[1]

    post_time_p = datetime.strptime(convert_to_datetime, '%H:%M')

    return post_time_p

def get_posts():
    ## post are in a div with class 'flex w-full flex-col text-xs'
    ## each post is in a div with class 'owner-data flex w-full items-start gap-3 pt-2'
    ## after every div with class 'owner-data flex w-full items-start gap-3 pt-2' there are siblings and they are part of the same post next post start with again 'owner-data flex w-full items-start gap-3 pt-2'
    ## get all post structure in a list

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    outer_div = soup.find('div', {'class': 'flex w-full flex-col text-xs'})

    posts = []

    ## get all div in outer_div
    for div in outer_div.find_all('div'):
        if div.get('class') == ['owner-data', 'flex', 'w-full', 'items-start', 'gap-3', 'pt-2']:
            post = []
            post.append(div)
            ## add below siblings to the same post
            for sibling in div.find_next_siblings():
                if sibling.get('class') == ['owner-data', 'flex', 'w-full', 'items-start', 'gap-3', 'pt-2']:
                    break
                else:
                    post.append(sibling)
            
            posts.append(post)
    
    return posts
        
def get_owner_name(post_part):
    ## get owner name
    owner_name = post_part.find('p', {'class': 'text-[14px] font-bold uppercase leading-[18px] text-[#2F2F2F] underline'}).text
    return owner_name

def get_locations(post_part):
    ## get locations
    anchors = post_part.find_all('a')
    anchors_text = [anchor.text.strip() for anchor in anchors]

    return {
        "game_type": anchors_text[0],
        "country": anchors_text[1],
        "league": anchors_text[2]
    }

def get_market(post_part):
    info_text = post_part.find('div', {'class': 'flex min-w-[100%] next-m:!min-w-[30px] pt-2 pb-2'}).text
    if '1X2' in info_text:
        market = '1X2'
    elif 'O/U' in info_text:
        market = 'O/U'
    elif 'AH' in info_text:
        market = 'AH'
    else:
        market = 'UNKNOWN'
    
    return market

def get_market_text(post_part):
    info_text = post_part.find('div', {'class': 'flex min-w-[100%] next-m:!min-w-[30px] pt-2 pb-2'})
    ps = info_text.find_all('p')
    return ps[-1].text.strip()

def get_game_time(post_part):
    info_text = post_part.find('div', {'class': 'flex min-w-[100%] next-m:!min-w-[30px] pt-2 pb-2'})
    ps = info_text.find_all('p')
    return ps[0].text.strip() + ' at ' + ps[1].text.strip()

def get_post_url(post_part):
    ## get post url
    url = post_part.find('a', {'class': 'flex w-full'}).get('href')
    return url

def get_pick(post_part, market_type):
    div = post_part.find('div', {'class': 'flex hover:bg-[#f9e9cc] group border-l border-r border-black-borders w-full'})
    divs = div.find_all('div', recursive=False)
    for index, div in enumerate(divs):
        if "PICK" in div.text:
            score = div.find_all('div', recursive=False)[0].text.strip()
            if market_type == '1X2':
                if index == 0:
                    return '1 @ ' + score
                elif index == 1:
                    return 'X @ ' + score
                elif index == 2:
                    return '2 @ ' + score
                else:
                    return 'UNKNOWN'
            elif market_type == 'O/U':
                if index == 0:
                    return 'Over @ ' + score
                elif index == 1:
                    return 'Under @ ' + score
                else:
                    return 'UNKNOWN'
            elif market_type == 'AH':
                if index == 0:
                    return '1 @ ' + score
                elif index == 1:
                    return '2 @ ' + score
                else:
                    return 'UNKNOWN'
            else:
                return 'UNKNOWN'

def get_game_opponents(post_part):
    div = post_part.find('div', {'class': 'relative w-full flex-col flex text-xs leading-[16px] min-w-[0] gap-1 next-m:!flex-row next-m:!gap-2 justify-center'})
    anchors = div.find_all('a')

    return {
        "first_opponent": anchors[0].text.strip(),
        "last_opponent": anchors[1].text.strip()
    }

def add_emoji(game_type):
    if game_type in ['Soccer', 'Football']:
        return '⚽️⚽️ ' + game_type + ' ⚽️⚽️'
    elif game_type == 'Basketball':
        return '🏀🏀 ' + game_type + ' 🏀🏀'
    elif game_type == 'Baseball':
        return '⚾️⚾️ ' + game_type + ' ⚾️⚾️'
    elif game_type == 'Hockey':
        return '🏒🏒 ' + game_type + ' 🏒🏒'
    elif game_type == 'Tennis':
        return '🎾🎾 ' + game_type + ' 🎾🎾'
    elif game_type == 'American football':
        return '🏈🏈 ' + game_type + ' 🏈🏈'
    else:
        return game_type
    
    

last_post_time = get_most_recent_post_time()
print("Starting time: ", last_post_time.time())

while True:
    sleep(random.randint(25, 35))
    print('Reloading page...', datetime.now().time())
    current_post_time = get_most_recent_post_time()

    if current_post_time > last_post_time:
        print('===============================')
        print('New post found!')

        ## get the newest post
        newest_post = get_posts()[0]
        
        ## check if market is relatable
        market = get_market(newest_post[4])
        if market == 'UNKNOWN':
            print('Unknown market!')            
            continue

        ## get owner name
        owner_name = get_owner_name(newest_post[0])

        locations = get_locations(newest_post[2])
        country = locations['country']
        league = locations['league']

        game_type = locations['game_type']
        game_type_with_emoji = add_emoji(game_type)
        game_time = get_game_time(newest_post[4])

        game_opponents = get_game_opponents(newest_post[4])
        first_opponent = game_opponents['first_opponent']
        last_opponent = game_opponents['last_opponent']

        market_text = get_market_text(newest_post[4])
        pick = get_pick(newest_post[4], market)
        post_url = get_post_url(newest_post[4])

        ## generate and send message
        message = f'{game_type_with_emoji}\n\nPick from {owner_name}\n\nMarket - {market_text}\n\n{pick}\n{first_opponent} v {last_opponent}\n{country} - {league}\n{game_time}\n\nhttps://www.oddsportal.com{post_url}'
        
        send_message(message)
        print('Message sent!')

    driver.refresh()