# This is a sample Python script.
import regrouppages
import splitepub
import splitpages
import striphtml
import tts

if __name__ == '__main__':
    splitepub.extract_epub_pages('./ebook.epub')
    splitpages.split_into_pages()
    striphtml.strip_html()
    regrouppages.regroup_pages()
    tts.convert()
