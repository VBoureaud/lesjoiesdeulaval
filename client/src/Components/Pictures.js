import Picture from '../Components/Picture';
import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import { config } from '../config';
import Request from 'superagent';
import _ from 'lodash';

class Pictures extends Component {
  constructor(){
    super();
    this.state = {};
  }

  /* Duplication with Picture.js -> API call file must be create */
  getPictures(url){
    Request.get(url).end((err, res) => {
      if (err || !res.ok) {
        this.setState({
          error: "Serveur injoinable",
          pictures: ''
        });
      }
      else if (res.status === 404) {
          this.setState({
          error: "404 - Page not found",
          pictures: ''
        });
      }
      else {
        var result = res.text.split(';')[0].replace(/\\/g, '').substr(1);
        var total = res.text.split(';')[1].substring(0, res.text.split(';')[1].length - 1);

        this.setState({
          error: '',
          pictures: JSON.parse(result),
          total: total
        });
      }
    });
  }

  componentWillMount()
  {
    this.setState({
      error: '',
      pictures: '',
      total: 0,
    });
    this.getPictures(config.apiUrl + this.props.location.pathname);
    this.setState({
      pathname: this.props.location.pathname
    });
    window.scrollTo(0, 0);
  }

  componentWillReceiveProps(newProps)
  {
    this.setState({
      error: '',
      pictures: '',
      total: 0,
    });
    this.getPictures(config.apiUrl + newProps.location.pathname);
    this.setState({
      pathname: newProps.location.pathname
    });
    window.scrollTo(0, 0);
  }

  render() {
    var pictures = _.map(this.state.pictures, (picture) => {
      return <Picture src={picture.url} title={picture.description} key={picture._id} id={picture._id} like={picture.like} date={picture.date} author={picture.author} />;
    })
    var error = "";
    if (this.state.error){
      error = <div className="error">{this.state.error}</div>
    }
    var loader = "";
    if (!this.state.pictures && !this.state.error){
      loader = <div className="loader"></div>
    }

    /* Pagination */
    var pathname = this.state.pathname.split('/')[1];
    /* Is not Homepage */
    if (isNaN(parseInt(pathname, 10)) && pathname !== ""){
      pathname = pathname + "/";
      var page = parseInt(this.state.pathname.split('/')[2], 10);
      if (page === undefined || isNaN(page)){page = 0;}
    }
    else {
      page = parseInt(this.state.pathname.substr(1), 10);
      pathname = "";
      if (page === "" || isNaN(page)){page = 0;}
    }

    /* Pagination display */
    if (page - 1 >= 0 && pathname !== "random/"){
      var url_prev = page - 1;
      var page_prev = <Link to={"/" + pathname + url_prev}><button type="button" className="btn btn-default btnLeft btn-lg">← Precedent</button></Link>;
    }
    if ((page + 1) * parseInt(config.perPage, 10) < parseInt(this.state.total, 10) && pathname !== "random/" && parseInt(this.state.total, 10) !== 0){
      var url_next = page + 1;
      var page_next = <Link to={"/" + pathname + url_next}><button type="button" className="btn btn-default btnRight btn-lg">Suivant →</button></Link>;
    }

    return (
      <div>
        {loader}
        {pictures}
        {error}
        <div className="container contain pagination">
          {page_prev}
          {page_next}
        </div>
      </div>
    );
  }
}

export default Pictures;
