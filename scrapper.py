import scrapy
import os


class Entrepreneur(scrapy.Spider):
  lang = 'en'
  name = "entrepreneur_scrapper"
  start_urls = [
    # 'https://www.entrepreneur.com/sitemaps/2018/January/us'
    # , 'https://www.entrepreneur.com/sitemaps/2018/February/us'
    # , 'https://www.entrepreneur.com/sitemaps/2018/February/us'
    # , 'https://www.entrepreneur.com/sitemaps/2018/March/us'
    # , 'https://www.entrepreneur.com/sitemaps/2018/April/us'
    # , 'https://www.entrepreneur.com/sitemaps/2018/May/us'

    # 'https://www.entrepreneur.com/sitemaps/2018/January/es'
    # , 'https://www.entrepreneur.com/sitemaps/2018/February/es'
    # , 'https://www.entrepreneur.com/sitemaps/2018/February/es'
    # , 'https://www.entrepreneur.com/sitemaps/2018/March/es'
    # , 'https://www.entrepreneur.com/sitemaps/2018/April/es'
    # , 'https://www.entrepreneur.com/sitemaps/2018/May/es', 


    'https://www.entrepreneur.com/article/222510'
    , 'https://www.entrepreneur.com/article/204854'
    , 'https://www.entrepreneur.com/article/178302'
    , 'https://www.entrepreneur.com/article/15574'
    , 'https://www.entrepreneur.com/article/238928'
    , 'https://www.entrepreneur.com/article/244990'
    , 'https://www.entrepreneur.com/article/236241'

    , 'https://www.entrepreneur.com/article/279987'
    , 'https://www.entrepreneur.com/article/250921'
    , 'https://www.entrepreneur.com/article/311307'
    , 'https://www.entrepreneur.com/article/246404'
    , 'https://www.entrepreneur.com/article/80204'
    , 'https://www.entrepreneur.com/article/288279'
    , 'https://www.entrepreneur.com/article/286697'

    , 'https://www.entrepreneur.com/article/28877'
    , 'https://www.entrepreneur.com/article/228125'
    , 'https://www.entrepreneur.com/article/236582'
    , 'https://www.entrepreneur.com/article/228541'
    , 'https://www.entrepreneur.com/article/307250'
    , 'https://www.entrepreneur.com/article/228534'
    , 'https://www.entrepreneur.com/article/302011'
    , 'https://www.entrepreneur.com/article/293281'
    , 'https://www.entrepreneur.com/article/236974'
    , 'https://www.entrepreneur.com/article/278180'

    , 'https://www.entrepreneur.com/article/311576'
    , 'https://www.entrepreneur.com/article/79254'
    , 'https://www.entrepreneur.com/article/298698'
    , 'https://www.entrepreneur.com/article/250973'
    , 'https://www.entrepreneur.com/article/303907'
    , 'https://www.entrepreneur.com/article/289979'
    , 'https://www.entrepreneur.com/article/284810'
    , 'https://www.entrepreneur.com/article/244873'
    , 'https://www.entrepreneur.com/article/54720'
    , 'https://www.entrepreneur.com/article/166076'

    , 'https://www.entrepreneur.com/article/288462'
    , 'https://www.entrepreneur.com/article/235947'
    , 'https://www.entrepreneur.com/article/284002'
    , 'https://www.entrepreneur.com/article/273619'
    , 'https://www.entrepreneur.com/article/310247'
    , 'https://www.entrepreneur.com/article/305188'
    , 'https://www.entrepreneur.com/article/52724'
    , 'https://www.entrepreneur.com/article/166076'
    , 'https://www.entrepreneur.com/article/219689'

    , 'https://www.entrepreneur.com/article/290617'
    , 'https://www.entrepreneur.com/article/290796'
    , 'https://www.entrepreneur.com/article/79254'
    , 'https://www.entrepreneur.com/article/41384'
    , 'https://www.entrepreneur.com/article/229459'
    , 'https://www.entrepreneur.com/article/271446'
    , 'https://www.entrepreneur.com/article/299773'
    , 'https://www.entrepreneur.com/article/76418'
    , 'https://www.entrepreneur.com/article/24380'
    , 'https://www.entrepreneur.com/article/290231'

    , 'https://www.entrepreneur.com/article/245217'
    , 'https://www.entrepreneur.com/article/80204'
    , 'https://www.entrepreneur.com/article/300293'
    , 'https://www.entrepreneur.com/article/279253'
    , 'https://www.entrepreneur.com/article/272540'
    , 'https://www.entrepreneur.com/article/245720'
    , 'https://www.entrepreneur.com/article/305600'
    , 'https://www.entrepreneur.com/article/279987'
    , 'https://www.entrepreneur.com/article/270230'

    , 'https://www.entrepreneur.com/article/278430'
    , 'https://www.entrepreneur.com/article/275696'
    , 'https://www.entrepreneur.com/article/240191'
    , 'https://www.entrepreneur.com/article/237712'
    , 'https://www.entrepreneur.com/article/285240'
    , 'https://www.entrepreneur.com/article/228566'
    , 'https://www.entrepreneur.com/article/245037'
    , 'https://www.entrepreneur.com/article/65028'
    , 'https://www.entrepreneur.com/article/237678'
                ]

  def getWebPageText(self, response):
    title_css = '.headline::text'
    title = response.css(title_css).extract_first().strip()

    intro_css = '.art-deck::text'
    intro = response.css(intro_css).extract_first()
    if intro:
      intro = intro.strip()
    else:
      intro = ''

    # body_xpath = '//*[@id="art-v2-container"]/section/div[5]'
    body_xpath = '//*[@id="art-v2-container"]/section/div'
    text_xpath = '//p//text()|//h3//text()'
    sentences = response.xpath(body_xpath).xpath(text_xpath).extract()
    startSent = ' button on any author page to keep up with the latest content from your favorite authors.'
    start = sentences.index(startSent) + 1
    endSent = 'Entrepreneur Media, Inc. values your privacy. In order to understand how people use our site generally, and to create more valuable experiences for you, we may collect data about your use of this site (both directly and through our partners). The table below describes in more detail the data being collected. By giving your consent below, you are agreeing to the use of that data. For more information on our data policies, please visit our '
    end = sentences.index(endSent)
    body = ' '.join(map(str.strip, sentences[start:end]))

    return title, intro, body

  def parse(self, response):
    ARTICLE_SELECTOR = '.nobullet.col3'
    my_list = response.css(ARTICLE_SELECTOR)

    if my_list:
      for article_name in my_list.xpath('li/a'):
        next_page = 'https://www.entrepreneur.com' + article_name.xpath('@href').extract_first().strip()
        if next_page:
          yield scrapy.Request(
            response.urljoin(next_page),
            callback=self.parse
          )
    else:
      title, intro, body = self.getWebPageText(response)
      filePath = os.path.join('/home/peregfe/projects/Entrepreneur/data/documents/new/' + self.lang, response.url.split('/')[-1] + '.txt')
      with open(filePath, 'w') as f:
        f.write(title + '\n' + intro + '\n' + body)
      self.log('Saved file %s' % filePath)