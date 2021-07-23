var app = new Vue({
  el: '#app',
  data: {
    drawer: false,
    textCopied: false,
    timeout: 6000,
    loadingToolsManifest : true,
    selectedTool: "",
    toolsManifest : []
  },
  mounted: function() {
    this.$nextTick(()=>{
      setTimeout(()=>{this.drawer = true},500)
    })
  },
  methods: {
    runTool: (resource)=>{

      let tool = app.toolsManifest.find((tool)=>{
        if (tool.resource === resource) {
          return tool
        }
      })
      console.log(tool.userInput.value)
      tool.inProgress = true
      tool.results = ""

      let xhr = new XMLHttpRequest()
      xhr.open('GET', `/api/tool/${resource}?${tool.userInput.name}=${tool.userInput.value}`, true)
      xhr.onprogress = (e)=>{
        tool.results = xhr.responseText
      }
      xhr.onload = (e)=>{
        if (xhr.readyState === 4) {
          if (xhr.status === 200) {
            console.log(xhr.responseText)
            tool.results = xhr.responseText
            tool.inProgress = false
          } else {
            console.error(xhr.statusText)
            tool.results = xhr.responseText
            tool.inProgress = false
          }
        }
      };
      xhr.onerror = function (e) {
        console.error(xhr.statusText)
      };
      xhr.send(null)
    }
  }
})

axios.get('/api/tools')
  .then((res)=>{
    app.loadingToolsManifest = false
    res.data.forEach((tool)=>{
      tool.inProgress = false
      tool.results = null
      tool.userInput.value = ""
      // add an isValid boolean
      tool.userInput.isValid = true
      // see if validation pattern provided
      if (tool.userInput.pattern) {
        // set isValid to false
        tool.userInput.isValid = false

        pattern = new RegExp(tool.userInput.pattern)
        // set up validation function
        tool.userInput.validate = (value)=>{
          if (pattern.test(value)) {
            tool.userInput.isValid = true
            return true
          } else {
            tool.userInput.isValid = false
            return 'Input invalid'
          }
          //return pattern.test(value) || 'Input invalid'
        }
      }
    })
    app.toolsManifest = res.data
  })
  .catch((err)=>{
    console.log(err)
  })
