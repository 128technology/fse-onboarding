'use strict'

const express = require('express')
const tools = require('./tools')
const app = express()
const port = 3006

app.use(express.static(`${__dirname}/public`))

app.listen(port, () => console.log(`Example app listening on port ${port}!`))

app.get('/api/tools', tools.getTools)

app.get('/api/tool/:tool', tools.runTool)
