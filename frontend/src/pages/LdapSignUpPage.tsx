import styles from './LdapSignUpPage.module.css'
import { useState } from 'react';
import CheckMark from '../components/AnimatedSymbols/CheckMark';

import axios from 'axios';

const LdapSignUpPage = () => {
  const [furthrAccount, setFurthrAccount] = useState(false);
  const [submitStatus, setSubmitStatus] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault()
    e.stopPropagation()

    if (e.target.checkValidity()) {
      const form = new FormData(e.target);
      const data = Object.fromEntries(form.entries());
      setSubmitStatus('submitting')
      axios.post('/web/ldap-signup', data).then(res => {
        setSubmitStatus('success')
      }).catch(err => {
        setSubmitStatus('error')
      })
    }

    e.target.classList.add('was-validated')
  }

  return (
    <div className={styles.formBg}>

      <main className={styles.signUpForm} >
        {submitStatus === 'error' && <p style={{ color: 'red' }}><b>An error has occured.</b></p>}
        {submitStatus === 'success' ? <CheckMark /> :
          <form onSubmit={handleSubmit} className="needs-validation" noValidate>
            <h5>Please enter your login information for your organization:</h5>
            <div className="mb-3">
              <label>Username</label>
              <input name='ldapuser' className='form-control' required />
            </div>
            <div className="mb-3">
              <label>Password</label>
              <input name='ldappassword' type='password' className='form-control' required />
            </div>
            <div className="mb-3">
              <label>Email</label>
              <input name='email' type='email' className='form-control' required />
            </div>
            <div className="form-check form-switch mb-3">
              <input className="form-check-input" type="checkbox" onChange={(e) => setFurthrAccount(e.target.checked)} />
              <label className="form-check-label">I already have a FURTHRmind account.</label>
            </div>
            {furthrAccount && <div className="mb-3">
              <label>FURTHRmind Password</label>
              <input name='furthrpassword' type='password' className='form-control' required={furthrAccount} />
            </div>}

            <input
              type="submit"
              className='btn btn-primary'
              disabled={submitStatus === 'submitting'}
              value={submitStatus === 'submitting' ? 'Submitting...' : 'Sign Up'}
            />
          </form>}
      </main>
    </div>
  );
}

export default LdapSignUpPage;
