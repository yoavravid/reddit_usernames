import itertools
from src.reddit_session import RedditSession


def main():
    with open('free_usernames.txt', 'a') as free_usernames:
        find_shortest_username(free_usernames)

def find_shortest_username(output_file):
    '''
    This function finds the shortest free user names on reddit.com, and stores them in output_file
    '''
    rs = RedditSession()
    rs.init()

    count = 0
    for i in range(3, 6):
        for username in itertools.product('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456790_', repeat=i):
            count += 1
            username_string = ''.join(username)
            if rs.is_username_free(username_string):
                print('username {} is free!'.format(username_string))
                output_file.write(username_string + '\n')
                output_file.flush()
            if count % 100 == 0:
                print('tried {} times'.format(count))


if __name__ == '__main__':
    main()