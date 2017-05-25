import ebooklib
import re
from ebooklib import epub
from lxml import html
from pprint import pprint

# book = epub.read_epub('/Users/brent/save/flavor-bible.epub')
# for item in book.get_items():
#     print(item.get_type(), item.get_name())

# with open('/Users/brent/tmp/test.html', 'wb') as f:
#     f.write(book.get_item_with_href('chapter003b.html').get_content())


# ebooklib.ITEM_DOCUMENT = 9
# 9 chapter003.html         intro
# 9 chapter003a.html        index
# 9 'chapter003b.html',        -content
# 9 'chapter003_a.html',       -content
# 9 'chapter003_1.html',       -content
# 9 'chapter003_2.html',       -content
# 9 'chapter003_2a.html',      -content
# 9 'chapter003_2b.html',      -content
# 9 'chapter003_3.html',       -content
# 9 'chapter003_4.html',       -content
# 9 'chapter003_5.html',       -content
# 9 'chapter003_6.html',       -content
# 9 'chapter003_6a.html',      -content

files = ['chapter003b.html',
         'chapter003_a.html',
         'chapter003_1.html',
         'chapter003_2.html',
         'chapter003_2a.html',
         'chapter003_2b.html',
         'chapter003_3.html',
         'chapter003_4.html',
         'chapter003_5.html',
         'chapter003_6.html',
         'chapter003_6a.html']


class Pairing:
    def __init__(self, source, target, rating):
        self.source_original = source
        self.target_original = target
        self.rating = rating
        self.source_category = None
        self.source_normal = None
        self.target_normal = None
        self.target_category = None

    def __str__(self):
        return ("{0.source_original}:{0.source_category}:{0.source_normal} -> "
                + "{0.target_original}:{0.target_normal}").format(self)

    def normalize(self):
        self._normalize_source()
        self._normalize_target()

    def _normalize_source(self):
        category = None
        normal = self.source_original.strip().lower()

        # special-cases
        cases = {'slow-cooked': 'slow cooking technique',
                 'beef—kobe': ('beef', 'kobe beef'),
                 'black-eyed peas': ('peas', 'black-eyed peas'),
                 'bonito flakes, dried': 'bonito flakes',
                 'cheese, goat—fresh': ('cheese', 'fresh goat cheese'),
                 'chocolate / cocoa': 'chocolate',
                 'crab, soft-shell': ('crab', 'soft-shell crab'),
                 'curry powder and sauces': 'curry powder',
                 'eggs, frittata': ('eggs', 'frittata'),
                 'eggs, hard-boiled': ('eggs', 'hard-boiled eggs'),
                 'eggs and eggbased dishes': 'eggs',
                 'five-spice powder': 'five-spice powder',
                 'french cuisine, northern': 'northern french cuisine',
                 'french cuisine, southern': 'southern french cuisine',
                 'georgian cuisine (russian)': 'georgian cuisine',
                 'italian cuisine, northern': 'northern italian cuisine',
                 'italian cuisine, southern': 'southern italian cuisine',
                 'lamb, chops': ('lamb', 'lamb chops'),
                 'lettuces—bitter greens and chicories': ('lettuces',
                                                          'bitter greens'),
                 'lettuces—mesclun greens': ('lettuces', 'mesclun greens'),
                 'melon/muskmelons': 'melons',
                 'mushrooms—chanterelles': ('mushrooms',
                                            'chanterelle mushrooms'),
                 'mushrooms—cremini': ('mushrooms', 'cremini mushrooms'),
                 'mushrooms—matsutake': ('mushrooms', 'matsutake mushrooms'),
                 'mushrooms—morels': ('mushrooms', 'morel mushrooms'),
                 'mushrooms—porcini / cepes / king bolete': ('mushrooms',
                                                             'porcini '
                                                             'mushrooms'),
                 'mushrooms—portobello': ('mushrooms', 'portobello mushrooms'),
                 'mushrooms—shiitake': ('mushrooms', 'shiitake mushrooms'),
                 'oatmeal / oats': 'oats',
                 'rice, arborio or carnaroli': ('rice', 'arborio rice'),
                 'salt, fleur de sel': ('salt', 'fleur de sel'),
                 'salt, sea—coarse': ('salt', 'coarse sea salt'),
                 'salt, sea—fine': ('salt', 'fine sea salt')}
        if normal in cases:
            case = cases[normal]
            if isinstance(case, str):
                normal = case
            else:
                category, normal = case
        else:
            # strip off in general
            normal = re.sub(r'[:]?[\-— ]in[\-— ]general', '', normal)

            # ex: american cuisine (southern) -> southern american cuisine
            cuisine_match = re.match(r'([^\(]+ )\(([^\)]+)\)', normal)
            if cuisine_match:
                normal = "{} {}".format(cuisine_match.group(2),
                                        cuisine_match.group(1))

            # ex: beef-steak: flank -> flank steak
            steak_match = re.match(r'([^\-—]+)[\-—]([^:]+): (.*)', normal)
            if steak_match:
                category = steak_match.group(1)
                normal = "{} {}".format(steak_match.group(3),
                                        steak_match.group(2))

            # ex: cheese, blue -> (cheese, blue cheese)
            comma_match = re.match(r'([^,]+), (.*)', normal)
            if comma_match:
                category = comma_match.group(1)
                normal = "{} {}".format(comma_match.group(2),
                                        comma_match.group(1))

            # ex: beef-brisket -> ('beef', 'beef brisket')
            comma_match = re.match(r'([^\-—]+)[\-—](.*)', normal)
            if comma_match:
                category = comma_match.group(1)
                normal = "{} {}".format(comma_match.group(1),
                                        comma_match.group(2))

        self.source_category = category or normal
        self.source_normal = normal

    def _normalize_target(self):
        normal = self.target_original.strip().lower()

        # strip off holy grail indicator
        normal = re.sub(r'^\*', '', normal)

        # special-cases
        cases = {'african (north) cuisine': 'north african cuisine',
                 'southern cuisine (american)': 'southern american cuisine',
                 'duck, legs': 'duck legs',
                 'eggs, yolk': 'egg yolks',
                 'egg, yolks': 'egg yolks',
                 'eggs, yolks': 'egg yolks',
                 'eggs, custard': 'egg custard',
                 'celery, leaves': 'celery leaves',
                 'legs, turkey': 'turkey legs',
                 'walnuts, oil': 'walnut oil',
                 'broccoli, rabe': 'broccoli rabe',
                 'sesame, seeds': 'sesame seeds',
                 'venison, shoulder': 'venison shoulder',
                 'liqueurs, berry or orange '
                 '(e.g., cointreau, curaçao, framboise, grand marnier': 'berry or orange liqueurs, such as cointreau, curaçao, framboise, or grand marnier',
                 'beans, esp. dried, summer (e.g., fava, green, lima)': 'beans, such as fava, green, or lima',
                 'caffeine (e.g., as in coffee, tea)': 'caffeine, as in coffee, tea',
                 'greens: bitter, dark leafy (e.g., beet, dandelion, mustard, turnip)': 'bitter, dark leafy greens, such as beet, dandelion, mustard, or turnip',
                 'lime, juice (e.g., indian cuisine)': 'lime juice, as in indian cuisine',
                 'liqueur, orange (e.g., grand marnier)': 'orange liqueur, such as grand marnier',
                 'liqueur, orange (e.g., grand marnier), peach': 'peach or orange liqueur, such as grand marnier',
                 'liqueur: almond (e.g., amaretto), hazelnut (e.g., frangelico), orange': 'almond, orange, or hazelnut liqueur, such as amaretto or frangelico',
                 'liqueurs, coffee (e.g., kahlúa, tía maria)': 'coffee liqueurs, such as kahlúa or tía maria',
                 'liqueurs: berry, coffee (e.g., kahlúa), nut (e.g., frangelico), orange': 'berry, coffee, nut, or orange liqueurs, such as frangelico',
                 'liqueurs: nut, orange, peach (e.g., schnapps)': 'nut, orange, or peach liqueurs, such as schnapps',
                 'liqueurs: nut, orange (e.g., cointreau, curaçao, grand marnier)': 'nut or orange liqueurs, such as cointreau, curaçao, or grand marnier',
                 'mexican cuisine (e.g., mole sauces)': 'mole sauces, as in mexican cuisine',
                 'onions: cooked, sweet (e.g., vidalia)': 'cooked sweet onions, such as vidalia',
                 'onions: fried, red, sweet (e.g., vidalia)': 'fried red or sweet onions, such as vidalia',
                 'oysters (e.g., stuffing)': 'oysters, as in stuffing',
                 'pumpkin (e.g., pie)': 'pumpkin, as in pie',
                 'rice (e.g., rice pudding) and risotto': 'rice, as in rice pudding or risotto',
                 'salads (e.g., fruit, green) and salad dressings': 'salads, such as fruit or green, and salad dressings',
                 'salads (e.g., green or tuna) and salad dressings': 'salads, such as green or tuna, and salad dressings',
                 'strawberries (e.g., fruit, puree)': 'whole or pureed strawberries',
                 'pasta, esp. richer egg-based and/or ribbon-shaped, often combined with other starches such as beans': 'pasta, especially richer egg-based and/or ribbon-shaped',
                 'bread, esp. indian (e.g., naan)': 'bread, such as indian naan',
                 'savory (e.g., as in french cuisine)': 'savory, as in french cuisine',
                 'garam masala (indian cuisine)': 'garam masala, as in indian cuisine',
                 'rose (french cuisine)': 'rose, as in french cuisine',
                 'chinese cuisine (e.g., as dessert)': 'chinese cuisine, such as dessert',
                 'cornmeal (e.g., as a crust)': 'cornmeal, as a crust',
                 'rice (e.g., as pudding)': 'rice, as in pudding',
                 'beef, in soup (pho)': 'beef soup, such as pho',
                 'm0starda (mustard fruits)': 'mostarda',
                 'malt (malted milk)': 'malted milk',
                 'bacon / lardons': 'bacon',
                 'pasta/noodles, egg': 'pasta or egg noodles',
                 'chile peppers: dried red (esp. sweet); fresh green': 'dried red or fresh green chile peppers',
                 'fruits, fruit compotes, and jams': 'fruits, fruit compotes, and jams',
                 'beef, short ribs': 'beef short ribs',
                 'breads, in the north': 'breads',
                 'cabbage, with corned beef brisket': 'cabbage',
                 'chicories, aka bitter greens': 'chicories',
                 'cream, half-and-half': 'cream or half-and-half',
                 'curries, curry paste, curry powder': 'curries',
                 'eggs, egg dishes, and omelets': 'eggs, egg dishes, and omelets',
                 'fruits, fruit compotes, and jams': 'fruits, fruit compotes, and jams',
                 'herbs, most other': 'herbs',
                 'lemon, juice, preserved': 'lemon juice',
                 'milk, including sweetened, condensed': 'milk, including sweetened condensed milk',
                 'orange, blood or regular, juice': 'oranges and orange juice',
                 'spirits, white: gin, vodka': 'white spirits, such as gin or vodka',
                 'stews, aka tagines': 'tagines',
                 }

        if normal in cases:
            case = cases[normal]
            if isinstance(case, str):
                normal = case
            else:
                category, normal = case
        else:
            # etc. ->
            normal = normal.replace(', etc.', '')

            # key ingredient ->
            normal = re.sub(r'\((.*?)ingredient(.*?)\)', '', normal)

            # parentheticals
            normal = re.sub(r' *\(.*?\)', '', normal)

            # / -> or
            if not re.search(r'and/or', normal):
                normal = re.sub(r' *\/ *', ' or ', normal)

            # (e.g., indian cuisine) -> as in indian cuisine
            cuisine_match = re.match(r'(.*?) \(e.g., (.*?) cuisine\)(.*?)', normal)
            if cuisine_match:
                lhs = cuisine_match.group(1)

                sep_match = re.match(r'(.*?)[,:] (.*)', lhs)
                if sep_match:
                    lhs = "{} {}".format(sep_match.group(2),
                                         sep_match.group(1))

                normal = "{}, as in {} cuisine{}".format(lhs,
                                                         cuisine_match.group(2),
                                                         cuisine_match.group(3))

            # e.g. -> such as
            eg_match = re.match(r'^([^(]+)\(e.g.,? ([^)]*)\)(.*)$', normal)
            if eg_match:
                normal = "{}, such as {}{}".format(eg_match.group(1).strip(),
                                                   eg_match.group(2),
                                                   eg_match.group(3))
            normal = normal.replace('e.g.,', 'such as')

            # esp. -> especially
            normal = normal.replace("esp.", "especially")

            # ex: juice, carrot -> carrot juice
            juice_match = re.match(r'^([^,]+), juice$', normal)
            if juice_match:
                normal = "{} {}".format(juice_match.group(1), "juice")

            # ex: zest, lime -> lime zest
            zest_match = re.match(r'^([^,]+), zest$', normal)
            if zest_match:
                normal = "{} {}".format(zest_match.group(1), "zest")

            # ex: butter, salted -> salted butter
            comma_match = re.match(r'^([a-z]+), *([a-z]+)$', normal)
            if comma_match:
                normal = "{} {}".format(comma_match.group(2),
                                        comma_match.group(1))

            # ex: zucchini (peak: july) -> zucchini
            comma_match = re.match(r'^([a-z]+) *\(peak:.*$', normal)
            if comma_match:
                normal = comma_match.group(1)

            # ex: zucchini (say some) -> zucchini
            comma_match = re.match(r'^([a-z]+) *\(say some\)$', normal)
            if comma_match:
                normal = comma_match.group(1)

            normal = normal.replace(',,', ',')

            # split at "such as"
            suchas_match = re.match(r'(.*?), such as (.*)', normal)
            if suchas_match:
                lhs = suchas_match.group(1)
                rhs = suchas_match.group(2)

                sep_match = re.match(r'(.*?)[,:] (.*)', lhs)
                if sep_match:
                    lhs = "{} {}".format(sep_match.group(2),
                                         sep_match.group(1))

                if not re.search(r'especially', lhs):
                    oxford_match = re.match(r'(.*?), ([^,]+)$', lhs)
                    if oxford_match:
                        comma = ""
                        if re.search(r',(.*?),', lhs):
                            comma = ","
                        lhs = "{}{} or {}".format(oxford_match.group(1),
                                                  comma,
                                                  oxford_match.group(2))

                if not re.search(r'especially', rhs):
                    oxford_match = re.match(r'(.*?), ([^,]+)$', rhs)
                    if oxford_match:
                        comma = ""
                        if re.search(r',(.*?),', rhs):
                            comma = ","
                        rhs = "{}{} or {}".format(oxford_match.group(1),
                                                  comma,
                                                  oxford_match.group(2))

                normal = "{}, such as {}".format(lhs, rhs)
            elif not re.search(r'as in', normal) and not re.search(r'especially', normal):
                comma_match = re.match(r'^([\w]+)[,] (.*)$', normal)
                if comma_match:
                    lhs = comma_match.group(1)
                    rhs = comma_match.group(2)

                    oxford_match = re.match(r'(.*?), ([^,]+)$', rhs)
                    if oxford_match:
                        comma = ""
                        if re.search(r',(.*?),', rhs):
                            comma = ","
                        rhs = "{}{} or {}".format(oxford_match.group(1),
                                                  comma,
                                                  oxford_match.group(2))

                    normal = "{} {}".format(rhs, lhs)
                else:
                    colon_match = re.match(r'^(.*?)[:] (.*)$', normal)
                    if colon_match:
                        lhs = colon_match.group(1)
                        rhs = colon_match.group(2)

                        # leading unnecessaries
                        if re.match(r'^nuts:', normal):
                            lhs = ''

                        oxford_match = re.match(r'(.*?), ([^,]+)$', rhs)
                        if oxford_match:
                            comma = ""
                            if re.search(r',(.*?),', rhs):
                                comma = ","
                            rhs = "{}{} or {}".format(oxford_match.group(1),
                                                      comma,
                                                      oxford_match.group(2))

                        # juice
                        if re.match(r'^juice', rhs):
                            lhs, rhs = rhs, lhs

                        normal = "{} {}".format(rhs, lhs)

            normal = re.sub(r'^especially ', '', normal)

        category = None
        self.target_category = category or normal
        self.target_normal = normal

    def split_source(self, source_normal):
        pairing = Pairing(self.source_original,
                          self.target_original,
                          self.rating)
        if self.source_category == self.source_normal:
            pairing.source_category = source_normal
        else:
            pairing.source_category = self.source_category
        pairing.source_normal = source_normal
        pairing.target_normal = self.target_normal
        return pairing

    def split_target(self, target_normal):
        pairing = Pairing(self.source_original,
                          self.target_original,
                          self.rating)
        if self.target_category == self.target_normal:
            pairing.target_category = target_normal
        else:
            pairing.target_category = self.target_category
        pairing.source_normal = self.source_normal
        pairing.target_normal = target_normal
        return pairing


def parse():
    result = []
    book = epub.read_epub('/Users/brent/save/flavor-bible.epub')
    for file in files:
        content = book.get_item_with_href(file).get_content()
        # with open('/Users/brent/tmp/flavor/{0}'.format(file), 'wb') as f:
        #     f.write(content)
        tree = html.fromstring(content)
        for ingredient in tree.xpath('.//h1'):
            source = ingredient.xpath('.//text()')
            if source:
                source = source[0]
                sibling = ingredient.getnext()
                while sibling is not None and sibling.tag != 'h1':
                    if sibling.xpath('*[.//text()="AVOID"]'):
                        break
                    if sibling.xpath('*[.//text()="Flavor Affinities"]'):
                        break
                    if sibling.get('class') in ['indentblock1', 'indentblock']:
                        for neighbor in sibling:
                            target = ''.join(neighbor.xpath('.//text()'))
                            if target[0] == '*':
                                rating = 1
                            elif target[:3].isupper():
                                rating = 2
                            elif neighbor.xpath('.//strong'):
                                rating = 3
                            else:
                                rating = 4
                            pairing = Pairing(source=source,
                                              target=target,
                                              rating=rating)
                            pairing.normalize()
                            result.append(pairing)
                    sibling = sibling.getnext()
    return result


def split_source(pairing):
    splitters = {'coconut and coconut milk': ['coconut', 'coconut milk'],
                 'coffee and espresso': ['coffee', 'espresso'],
                 'kaffir limes and kaffir lime leaf': ['kaffir limes',
                                                       'kaffir lime leaves'],
                 'miso and miso soup': ['miso', 'miso soup'],
                 'peanuts and peanut butter': ['peanuts', 'peanut butter']}
    for normal in splitters.get(pairing.source_normal,
                                [pairing.source_normal]):
        yield pairing.split_source(normal)


def split_target(pairing):
    normal = pairing.target_original.strip().lower()
    splitters = {'african cuisine bacon': ['african cuisine', 'bacon'],
                 'apples, esp. golden delicious or granny smith, and apple cider artichoke hearts': ['apples, especially golden delicious or granny smith', 'apple cider', 'artichoke hearts'],
                 'shellfish, shrimp': ['shellfish', 'shrimp'],
                 'fish, white (e.g., cod, halibut) garam masala (e.g., indian cuisine)': ['white fish, such as cod, halibut', 'garam masala, as in indian cuisine'],
                 'greens (e.g., chard, spinach) ham, serrano': ['greens, such as chard, spinach', 'serrano ham'],
                 'olives (e.g., green) onions, esp. red or': ['olives, such as green', 'onions, especially red or yellow', 'oregano', 'paprika', 'smoked flat-leaf parsley', 'pasta'],
                 'rice (e.g., pudding) rum': ['rice, such as pudding', 'rum'],
                 'tabbouleh (key ingredient) tarragon': ['tabbouleh', 'tarragon'],
                 '(esp. red)': [],
                 'cloves (compatible spice) cookies': ['cloves', 'cookies'],
                 'chile peppers, chipotle—use adobo sauce from canned chiles': ['chile peppers', 'chipotle chiles in adobo'],
                 'cocktails: mint julep (ingredient), pimms no. 1 cup (ingredient)': ['mint julep', 'pimms cup'],
                 'parsley, flat-leaf pepper: black, white': ['flat-leaf parsley', 'black pepper', 'white pepper'],
                 'bread, bread crumbs': ['bread', 'bread crumbs'],
                 'bread, breadsticks, croutons, etc.': ['bread', 'breadsticks', 'croutons'],
                 'butter, unsalted calvados': ['unsalted butter', 'calvados'],
                 'butter, unsalted caramel cardamom cashews': ['unsalted butter', 'caramel', 'cardamom', 'cashews'],
                 'butter, unsalted celery': ['unsalted butter', 'celery'],
                 'cheese, cheddar ham marinades meats': ['cheddar', 'ham', 'marinades', 'meats'],
                 'currants, black or red: fruit, preserves': ['currants', 'fruit preserves'],
                 'currants, red: fruit, jelly': ['currants', 'fruit jelly'],
                 'pepper, black pork': ['black pepper', 'pork'],
                 'pepper, red ground pickles': ['red ground pepper', 'pickles'],
                 'potatoes, french fries': ['potatoes', 'french fries'],
                 'seafood, heartier soups': ['seafood', 'heartier soups'],
                 'sherry, dry (e.g., fino) soy sauce': ['dry sherry', 'soy sauce'],
                 'sugar, brown thyme': ['brown sugar', 'thyme'],
                 'tomatoes, tomato juice, tomato paste': ['tomatoes', 'tomato juice', 'tomato paste'],
                 'tomatoes, tomato juice, tomato sauce': ['tomatoes', 'tomato juice', 'tomato sauce'],
                 'tomatoes, tomato paste, and tomato sauce': ['tomatoes', 'tomato paste', 'tomato sauce'],
                 'truffles, black, and truffle oil': ['black truffles', 'truffle oil'],
                 'vegetables, root vinaigrettes': ['root vegetables', 'vinaigrettes'],
                 'wine, red, and red wine sauces': ['red wine', 'red wine sauces'],
                 'walnuts: nuts, oil': ['walnuts', 'walnut oil'],
                 'fruit: apples, pears': ['apples', 'pears'],
                 'fruits: fruit compotes, fruit desserts': ['fruit compotes', 'fruit desserts'],
                 'tomatoes: cherry, grape, juice, roasted': ['cherry tomatoes', 'grape tomatoes', 'tomato juice', 'roasted tomatoes'],
                 'apples: cider, juice': ['apple cider', 'apple juice'],
                 'apple: cider, fruit, juice': ['apple cider', 'apples', 'apple juice'],
                 'apples: cider, fruit, juice': ['apple cider', 'apples', 'apple juice'],
                 'apples: cider, fruit, juice buckwheat (key ingredient in crepes)': ['apple cider', 'apples', 'apple juice', 'buckwheat'],
                 'lemon: confit, juice, zest': ['lemon confit', 'lemon juice', 'lemon zest'],
                 'tomatoes: flesh, juice': ['tomatoes', 'tomato juice'],
                 '*apples: fruit, juice': ['apples', 'apple juice'],
                 'apples: fruit, juice': ['apples', 'apple juice'],
                 'orange: fruit, juice': ['oranges', 'orange juice'],
                 'lemon: fruit, juice, zest': ['lemonts', 'lemon juice', 'lemon zest'],
                 'orange: fruit, juice, zest': ['oranges', 'orange juice', 'organge zest'],
                 'coconut: fruit, milk, water': ['coconut', 'coconut milk', 'coconut water'],
                 'orange: juice, zest oregano': ['orange juice', 'orange zest', 'oregano'],
                 }
    for normal in splitters.get(normal,
                                [pairing.target_normal]):
        yield pairing.split_target(normal)


def split_pairings(pairings):
    for pairing in pairings:
        for source_pairing in split_source(pairing):
            for target_pairing in split_target(source_pairing):
                yield target_pairing


pairings = split_pairings(parse())
print()
for pairing in sorted({(p.source_normal, p.rating, p.target_normal)
                       for p in pairings}):
    print("{0:60} {1} {2}".format(*pairing))
