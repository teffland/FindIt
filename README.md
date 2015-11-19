# FindIt
Weakly supervised context focused web crawler for disparate seed domains

**DISCLAIMER: This project was done for a [research project](http://src.acm.org/2015/ThomasEffland.pdf) in my senior year of undergrad.**
After the submission I never did the refactoring necessary to make it really usable for open source. It had potential but due to shifting interests, I never got back to this.
As such, the code is not clean (anyone who has had a submission deadline can hopefully sympathize), the training data chrome extension has bugs, and the framework has been left in a torn up state.
**Feel free to use any of it, but please do so at your own risk.**

### The goal of FindIt
Say you have domain names of a bunch of websites and you know that the content that you want lies somewhere in the depths of each of these websites, but you don't know exactly where they are.

You could go find all of these pages manually, but at scale you'd rather automate it.

FindIt is a tool designed to find these pages for you! 

All you have to do is show it a few samples of you finding the pages yourself, and it will learn how to find the other pages using machine learning.

### An Example: University Course Descriptions
Say you want to get the course descriptions pages from lots of universities. Findit can help do this automatically.

Using a chrome extension MarkIt (packaged with FindIt), first you find a few of these pages yourself by navigating from the root url to a course descriptions page.

MarkIt will record these sample traverals as training data.

Then you let FindIt go out and gather lots of unlabeled pages from these websites.

With all of this unlabeled data, and a small labeled sample, FindIt uses semi-supervised machine learning to train itself!

After training, just give FindIt a set of websites that you want data from, and let FindIt find it or you.

For more details, check out the [paper](http://src.acm.org/2015/ThomasEffland.pdf)

