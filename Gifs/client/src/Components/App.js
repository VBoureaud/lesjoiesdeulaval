import React, { Component } from 'react';
import { Navbar } from 'react-bootstrap';
import { Switch, Route, Link } from 'react-router-dom';
import Pictures from '../Components/Pictures';
import Picture from '../Components/Picture';
import Add from '../Components/Add';

/* Google Analytics */
var ReactGA = require('react-ga');
ReactGA.initialize('UA-108797290-1');

function NavbarInstance(props) {
  return (
    <Navbar className="navbarApp">
      <Navbar.Header>
        <Navbar.Brand>
          Les joies de ULaval
        </Navbar.Brand>
      </Navbar.Header>
      <div className="linkNav">
        <Link className="link_red navbarLink glyphicon glyphicon-download" to="/">Dernier gifs</Link>
        <Link className="link_blue navbarLink glyphicon glyphicon-heart" to="/best">Les meilleurs</Link>
        <Link className="link_yellow navbarLink glyphicon glyphicon-random" to="/random">Aleatoire</Link>
        <Link className="link_blue2 navbarLink glyphicon glyphicon-upload" to="/send">Envoie ton gif</Link>
        <a className="link_blue navbarLink social_navbar" href="https://www.facebook.com/Les-joies-de-Ulaval-1570536933006817"><span className="fa fa-facebook"></span></a>
      </div>
    </Navbar>
  );
}

function logPageView() {
    ReactGA.set({ page: window.location.pathname });
    ReactGA.pageview(window.location.pathname);
    return null;
}

class App extends Component {
  constructor(props) {
    super();
  }

  render() {
    return (
      <div className="App">
        <NavbarInstance />
        <main>
          <Route path="/" component={logPageView} />
          <Switch>
            <Route exact path="/" component={Pictures} />
            <Route exact path="/send" component={Add} />
            <Route exact path="/:page_id" component={Pictures} />
            <Route path="/picture/:picture_id" component={Picture} />
            <Route exact path="/best" component={Pictures} />
            <Route exact path="/best/:page_id" component={Pictures} />
            <Route exact path="/random" component={Pictures} />
          </Switch>
        </main>
      </div>
    );
  }
}

export default App;