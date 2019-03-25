import React, { Component } from 'react';
import Request from 'superagent';
import { FormGroup, ControlLabel, FormControl, HelpBlock, Button } from 'react-bootstrap';
import { config } from '../config';

function FieldGroup({ id, label, help, ...props }) {
  return (
    <FormGroup controlId={id}>
      <ControlLabel>{label}</ControlLabel>
      <FormControl {...props} />
      {help && <HelpBlock>{help}</HelpBlock>}
    </FormGroup>
  );
}

class Add extends Component {
  constructor(){
    super();

    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleFileChange = this.handleFileChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);

    this.state = {}
  }

  handleInputChange(event){
    const target = event.target;
    const name = target.name;

    if (target.name){
      this.setState({
            [name]: target.value
      });
    }
  }

  handleFileChange(event){
    const file = event.target.files[0];
    this.setState({file: file});
  }

  handleSubmit(e){
    e.preventDefault();
    var self = this;

    this.setState({
      loader: true,
    })

    /* Check error */
    if (!this.state.auteur || !this.state.phrase || 
        !this.state.file){
      var errDisplay = <div className="error error_gifPage">Erreur - </div>
      this.setState({error: errDisplay, success: '', loader: false});
      return false;
    }

    /* Gestion send */
    var formData = new FormData();
    formData.append('author', this.state.auteur);
    formData.append('description', this.state.phrase);
    formData.append('picture', this.state.file);
    Request.post(config.apiUrl + '/upload')
           .send(formData)
           .end(function(err, response) {
              if (err) {
                var errDisplay = <div className="error error_gifPage">Erreur<br />L'image n'est pas un gif ou trop lourde, ou bien le champ login et phrase ne sont pas correctement remplis</div>
                self.setState({error: errDisplay, success: '', loader: false});
                return false;
              } else {
                  var success = <div className="error error_gifPage success_gifPage">Image envoyée<br />En attente de validation</div>
                  self.setState({success: success, error: '', loader: false});
              }
           });

    /* Reset */
    this.setState({
      auteur: '',
      phrase: '',
      file: '',
    })
    e.target.reset();
  }

  render() {
      var loader = "";
      if (this.state.loader){
        loader = <div className="loader"></div>
      }
      return (
        <div>
          {loader}
          <div className="container gifBox addGif">
              {this.state.error}
              {this.state.success}
              <h3>Envoie nous ton gif</h3>
              <form onSubmit={this.handleSubmit}>
                  <FieldGroup
                    id="formControlsText"
                    type="text"
                    label="Ta phrase"
                    name="phrase"
                    required
                    placeholder="Ex : Quand il n'y a plus qu'à..."
                    onChange={this.handleInputChange}
                  />
                  <FieldGroup
                    id="formControlsText"
                    type="text"
                    label="Ton login / pseudo"
                    name="auteur"
                    required
                    placeholder="Ex: ULaval"
                    onChange={this.handleInputChange}
                  />
                  <FieldGroup
                    id="formControlsFile"
                    type="file"
                    label="File"
                    accept="image/gif"
                    name="file"
                    required
                    onChange={this.handleFileChange}
                    help="On accepte seulement les GIFs & du bon français."
                  />
                  <Button type="submit">
                      Envoyer
                  </Button>
              </form>
          </div>
        </div>
      );
  }
}

export default Add;
