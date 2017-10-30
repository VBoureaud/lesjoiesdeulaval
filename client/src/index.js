import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom';
import App from './Components/App';

import './Css/App.css';
import './Css/bootstrap-social.css';

const my_app = document.getElementById('root');

ReactDOM.render((
    <BrowserRouter>
        <App />
    </BrowserRouter>
), my_app);
