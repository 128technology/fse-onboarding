'use strict'

const fs = require('fs')
const { spawn } = require('child_process')
const toolsManifest = `${__dirname}/tools-manifest.json`
var toolRunInProgress = false

function readToolsManifest() {
  return new Promise((resolve, reject) => {
    fs.readFile(toolsManifest, (err, data) => {
      if (err) {
        // unable to read the file
        reject(err)
      } else {
        try {
          let parsedData = JSON.parse(data)
          // resolve with data parsed to object
          resolve(parsedData)
        } catch (err) {
          // unable to parse file data as JSON
          reject(err)
        }
      }
    })
  })
}

function getTools(req, res, next) {
  readToolsManifest()
    .then((toolsManifest) => {
      res.send(toolsManifest)
    })
    .catch((err) => {
      next(err)
    })
}

function runTool(req, res, next) {
  // get tool from tool manifest object
  let requestedTool = req.params.tool

  readToolsManifest()
    .then((toolsManifest) => {
      let matchedTool = toolsManifest.find((manifestTool) => {
        if (manifestTool.resource === requestedTool) {
          return manifestTool
        }
      })

      if (!matchedTool) {
        return Promise.reject({ code: 404, message: "Tool not found" })
      } else {
        return Promise.resolve(matchedTool)
      }
    })
    .then((tool) => {

      // validate query
      // console.log(req.query)
      let queryName = Object.keys(req.query)[0]
      let queryValue = req.query[queryName]
      // console.log(`query name "${queryName}", query value "${queryValue}"`)
      // console.log(tool.userInput)
      try {
        if (!tool.userInput.name === queryName) {
          console.log(`"${queryName}" does not match "${tool.userInput.name}"`)
          return Promise.reject({ code: 400, message: "Invalid query parameter" })
        }
        // set up regex based on pattern specified in tool
        let pattern = new RegExp(tool.userInput.pattern)

        if (!pattern.test(queryValue)) {
          console.log(`query value "${queryValue}" does not pass validation pattern "${pattern}"`)
          return Promise.reject({ code: 400, message: "Invalid query parameter value" })
        }
      } catch (err) {
        return Promise.reject({ code: 500, message: "Error processing query parameter" })
      }

      // Inputs are validated...begin setting up response
      res.setHeader('Connection', 'Transfer-Encoding')
      res.setHeader('Content-Type', 'text/html; charset=utf-8')
      res.setHeader('Transfer-Encoding', 'chunked')
      res.setHeader('X-Content-Type-Options', 'nosniff')

      // check to see if tool run is in progress
      if (toolRunInProgress) {
        return Promise.reject({ code: 500, message: "Automation tool job in progress. Please try again later." })
      } else {
        toolRunInProgress = true
      }

      try {
        console.log(`spawning ${tool.script}.`)

        let processArgs = []
        if (tool.args && Array.isArray(tool.args)) {
          processArgs = tool.args
        }
        processArgs.push(queryValue)
        let options = { env: { LANG: 'en_US.UTF-8', LC_ALL: 'en_US.UTF-8' } }
        let process = spawn(`${__dirname}${tool.script}`, processArgs, options)

        process.stdout.on('data', (data) => {
          //console.log(`stdout: ${data}`)
          res.write(data)
        })

        process.stderr.on('data', (data) => {
          console.log(`stderr: ${data}`)
          //  res.write(data)
        })

        process.on('error', (err) => {
          console.log(err)
          //res.status(501).send(`failed to launch process: ${err}`)
        })

        process.on('close', (code) => {
          toolRunInProgress = false
          console.log(`${tool.script} exit with code ${code}.`)
          if (code != 0) {
            res.status(500).send(`Process exited with error code ${code}.`)
          } else {
            res.end()
          }
        })

      } catch (err) {
        console.log(err)
        return Promise.reject({ code: 500, message: "Could not spawn process" })
      }

      //res.send(tool)
    })
    .catch((err) => {
      toolRunInProgress = false
      res.status(err.code || 500).send(err.message || err)
      res.end()
    })

}

exports.getTools = getTools
exports.runTool = runTool
