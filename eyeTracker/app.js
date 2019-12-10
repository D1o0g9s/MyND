const express = require('express')

// Create Express app
const app = express()

// A sample route
app.get('/', (req, res) => res.send('Hello World!'))

// Start the Express server
app.listen(3000, () => console.log('Server running on port 3000!'))

app.use(express.static('public'));