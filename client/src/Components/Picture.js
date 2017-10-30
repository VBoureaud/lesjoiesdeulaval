import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import { config } from '../config';
import Request from 'superagent';

class Picture extends Component {
  constructor(){
    super();
    this.state = {
      error: '',
      id: '',
      title: '',
      src: '',
      like: '',
      date: 0,
      author: '',
    };

    this.handleLike = this.handleLike.bind(this);
  }

  /* Duplication with Pictures.js -> API call file must be create */
  getPictures(url){
    Request.get(url).end((err, res) => {
      if (err || !res.ok) {
        this.setState({
          error: "Serveur injoinable"
        });
      }
      else if (res.status === 404) {
          this.setState({
          error: "404 - Page not found"
        });
      }
      else {
        var result = JSON.parse(res.text)
        if (result._id !== undefined){
          this.setState({
            error: '',
            id: result._id,
            title: result.description,
            src: result.url,
            date: result.date,
            like: result.like,
            author: result.author,
          });
        }
      else
        this.setState({error: 'Aucun résultat'});
      }
    });
  }

  componentWillMount(){
    if (this.props.match){
      this.getPictures(config.apiUrl + "/picture/" + this.props.match.params.picture_id);
    }
    else {
        this.setState({
          id: this.props.id,
          title: this.props.title,
          src: this.props.src,
          like: this.props.like,
          date: this.props.date,
          author: this.props.author,
        });
    }
  }

  handleLike() {
    var self = this;
    Request.post(config.apiUrl + '/like')
           .send({ id_post: this.state.id })
           .end(function(err, res) {
              if (!err && res.status !== 202) {
                self.setState({
                  like: self.state.like + 1
                });
              } else if (res.status === 202) {
                self.setState({
                  everLike: <p>Post déjà liké</p>
                });
              }
           });
  }

  render() {
    if (this.state.error === ''){
      const img_url = this.state.src;
      return (
        <div className="picture contain container">
          <div className="date">
            <span>{new Date(this.state.date).getDate()}</span>
            <span>{config.monthNames[new Date(this.state.date).getMonth()]}</span>
          </div>
          <div className="gifBox">
              <h3><Link to={"/picture/" + this.state.id}>{this.state.title}</Link></h3>
              <div className="imgIllustration"><img src={img_url} alt={this.state.title} /></div>
          </div>
          <div className="author">
          <p>proposé par <strong>{this.state.author}</strong></p>
          </div>
          <div className="containLeft">
             <a className="btn btn-social btn-facebook" href={"https://www.facebook.com/sharer/sharer.php?kid_directed_site=0&sdk=joey&u=" + encodeURIComponent(config.clientUrl + "/picture/" + this.state.id)}>
              <span className="fa fa-facebook"></span> Partager
            </a>
            <a className="btn btn-social btn-twitter" href={"https://twitter.com/intent/tweet?original_referer=" + encodeURIComponent(config.clientUrl + "/picture/" + this.state.id) + "&ref_src=twsrc%5Etfw&text=" + encodeURIComponent(this.state.title) + "&tw_p=tweetbutton&url=" + encodeURIComponent(config.clientUrl + "/picture/" + this.state.id)}>
              <span className="fa fa-twitter"></span> Partager
            </a>
            <div className="like">
              <span>{this.state.like}</span>
              <a className="btn btn-like" onClick={this.handleLike}>
                <span className="fa fa-heart"></span>
              </a>
              {this.state.everLike}
            </div>
          </div>
        </div>
      );
    }
    else {
      return (
        <div className="error">{this.state.error}</div>
      );
    }
  }
}

export default Picture;
