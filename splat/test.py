import main
import crawler

print(crawler.parse_challenge()[0])
print(crawler.parse_challenge()[1])
print(crawler.ranked[0])
print('aaaa')
lg = crawler.ranked[0]["bankaraMatchSettings"][0]['vsStages'][1]
print(lg)
print(crawler.translate_stage(lg["id"]))