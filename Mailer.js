import express, { json } from 'express';
import { createTransport } from 'nodemailer';
import cors from 'cors';

const app = express();
app.use(json());
app.use(cors());
3.
const transporter = createTransport({
  service: 'gmail', 
  auth: {
      user: '',  
      pass: ''          
  }
});

app.post('/send-email', (req, res) => {
  const { from, subject, text } = req.body;

  const mailOptions = {
    to: 'asgarovravan@gmail.com',  
    from: `${from} <asgarovravan@gmail.com>`, 
    subject,
    text: `Sender: ${from}\n\n${text}`  // Corrected template literal for text content
  };

  transporter.sendMail(mailOptions, (error, info) => {
    if (error) {
      return res.status(500).json({ message: 'Error sending email', error });
    }
    res.status(200).json({ message: 'Email sent', info });
  });
});



const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log('Server running on port http://127.0.0.1:3001');
});
