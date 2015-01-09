Pelletron
===

**Pelletron** is yet another static site generator. Every modern programmer must reinvent this particular wheel.

Description
---

Pelletron aims to minimize the effort of creating rich content, imposing as little overhead as possible to provide this power.

Pelletron is written in [Python](https://www.python.org/). [Jinja2](http://jinja.pocoo.org/docs/dev/) is its templating language. [Flask](http://flask.pocoo.org/) is the glue, providing utilities to build, serve (while debugging), and deploy the static pages. The [FlatPages](https://pythonhosted.org/Flask-FlatPages/) extension defines page content, using [YAML](http://yaml.org/spec/1.1/) to define the structure. It supports [Markdown](http://daringfireball.net/projects/markdown/syntax) for text formatting and [pygments](http://pygments.org/) for code syntax highlighting. The [Frozen-Flask](http://pythonhosted.org/Frozen-Flask/) extension converts the templates to static pages.

Pelletron lets you preview your site using Flask's built-in development server, and includes [Flask-DebugToolbar](http://flask-debugtoolbar.readthedocs.org/en/latest/).

[Rsync](https://en.wikipedia.org/wiki/Rsync) handles deployment to the target server.

Override the skeleton starter templates with widely used HTML5 frameworks such as Bootstrap, Foundation, and HTML5 Boilerplate. (See **Beyond bare bones** below for more information.)

Installation
---

For **Linux** and **OS X**:

- Clone this repository:
  - $ `git clone git@github.com:jeffkayser/pelletron.git`
- Create a new python virtual environment:
  - $ `mkvirtualenv my-site`
- Ensure you're using the new virtual environment:
  - $ `workon my-site`
- Install the requirements:
  - $ `pip install -r requirements.txt`
- Test the site build process:
  - $ `python site.py build`
  - You may see some warnings; it's safe to ignore them
- Test the server:
  - $ `python site.py server`
  - Use your web browser to navigate to `http://localhost:5050`
  - You should see a page with the following text at the top appear:
    > **Pelletron is working**
- Deploy to localhost as the current user:
  - $ `python site.py deploy`
  - Edit `config.py` to change deployment options such as host, username, and path.

Usage
---

	.
	|-- built/               <-- Final static site output
	|-- config.py            <-- Set configuration options
	|-- framework.py         <-- Framework name currently in use
	|-- site.py              <-- Site management utility
	`-- source/              <-- User defined content goes here
	    |-- controller.py    <-- MVC controllers (blank by default)
	    |-- model.py         <-- MVC models (blank by default)
	    |-- modules/         <-- Holds modules such as front-end frameworks
	    |   |-- bootstrap/
	    |   |-- custom/
	    |   |-- foundation/
	    |   `-- html5boilerplate/
	    |-- pages/           <-- Holds 'page' content
	    |   `-- home.md      <-- Sample 'page'
	    |-- static/          <-- Static content goes here (favicon, css, javascript, etc.)
	    |-- templates/       <-- Page layout
	    `-- view.py          <-- MVC views (includes URL route mappings)

Beyond bare bones
---

Vanilla Pelletron is not opinionated beyond its basic technical structure, which is optimized for content not design, and provides none of the common HTML5 frameworks popular as jump-off points today. However, modules for the following frameworks are available for your use immediately:

- [Boostrap](http://getbootstrap.com/)
- [Foundation](http://foundation.zurb.com/)
- [HTML5 Boilerplate](http://html5boilerplate.com/)

These frameworks can give you a much stronger jumping off point if your site's design needs match up with their respective authors' choices.

Copyright and License
---

Copyright &copy; 2015 Jeff Kayser. Released under the MIT license.