/**
 * Launches HTML interface
 */
function doGet() {
  return HtmlService.createHtmlOutputFromFile("Index")
}


/** 
 * Creates a new Google Form for the provided set of Tweets.
 * Returns unique form ID and URL to the created Form
 * 
 * @param {string} formName
 * @param {string} tweetsToAnnotate
 * @param {string} knownRumours
 * @return {string}
 */
function generateAnnotationForm(formName, tweetsToAnnotate, knownRumours) {
  // Check that JSONS are formatted correctly
  if (badlyFormattedParameters(formName, tweetsToAnnotate, knownRumours)) {
    return "Check that the fields are filled out and the JSON strings are structured correctly!"
  }

  var description = "This form contains a set of social media posts, ready for annotation. " +
                    "You will be asked to determine which category a tweet belongs to, " +
                    "and which COVID-19 rumour it discusses."

  try {

    // Create form with title
    var form = FormApp.create(formName)
      .setTitle(formName)
      .setDescription(description)
      .setCollectEmail(true)
      .setProgressBar(true)
      .setLimitOneResponsePerUser(true)
      .setAllowResponseEdits(true)
      .setRequireLogin(false)
      .setPublishingSummary(true)

    // Create spreadsheet destination
    var destination = SpreadsheetApp.create(formName + "_responses")
    moveFile(destination.getId())
    form.setDestination(FormApp.DestinationType.SPREADSHEET, destination.getId())

    moveFile(form.getId()) // move to shared drive folder
    writeFormLog(form, formName) // write ID and URLs to sheet


    // ~~~ CONSTRUCT QUESTIONS ~~~ //
    
    // Parse JSON strings
    var tweetsJSON = JSON.parse(tweetsToAnnotate)
    var rumours = JSON.parse(knownRumours)

    // Check tweet array is defined
    var tweets = tweetsJSON.tweetSample
    if (tweets == null || tweets == undefined) {
      return 'Tweets to Annotate doesn\'t contain a root "tweetSample" property!'
    }

    // For numeric answer questions
    var numericValidation = FormApp.createTextValidation()
      .setHelpText('Input must be a number between 0 and 100.')
      .requireNumberBetween(0, 100)
      .build()
    
    // Participant ID number
    var participantNumberQ = form.addTextItem()
      .setTitle('Participant ID')
      .setHelpText('Your unique participant number, provided when you signed up for the study.')
      .setRequired(true)
      .setValidation(numericValidation)


    // ~~~ NEW PAGE FOR EACH TWEET ~~~ //

    // For each tweet, create a new annotation question
    for (let i = 0; i < tweets.length; i++) {
      // New page
      form.addPageBreakItem()
        .setTitle("Rumour Identification")
        .setHelpText("Please annotate which rumour is being discussed in the Tweet text.")

      var tweet = tweets[i]
      var question = form.addMultipleChoiceItem();
      
      question.setTitle(tweet.text)
      // question.setHelpText('#' + (i+1) + " id: " + tweet.tweetID)

      // Get rumour shortlist
      var shortlistedRumours = parseShortlist(tweet, rumours)

      // Add text descriptions to question
      var choices = shortlistedRumours.map(r => { return r.description })
      choices.push('Other: rumour not listed')
      choices.push('Other: does not discuss a rumour')
      question.setChoiceValues(choices)
    }
  }
  catch (error) {
    return error
  }

  Logger.log('Published URL: ' + form.getPublishedUrl())
  Logger.log('Editor URL: ' + form.getEditUrl())

  return 'Success! <a href=' + form.getPublishedUrl() + ' target="_blank">View Generated Form</a>'
}

/**
 * Returns true if parameters are invalid, else false
 * @return {bool}
 */
function badlyFormattedParameters(formName, tweetsToAnnotate, knownRumours) {
  // Check exists
  if (formName == null || formName == undefined || formName == "" ||
      tweetsToAnnotate == null || tweetsToAnnotate == undefined || tweetsToAnnotate == "" ||
      knownRumours == null || knownRumours == undefined || knownRumours == "") {
      return true;
  }

  // Check JSON parsable
  try {
    JSON.parse(tweetsToAnnotate)
    JSON.parse(knownRumours)
  }
  catch (ex) {
    return true
  }

  return false;
}

/**
 * Return a list of rumours for the given tweet
 */
function parseShortlist(tweet, rumours) {
  var shortlist = []

  // For each rumour in the shortlist...
  var shortlistedIDs = tweet.rumourShortlist
  for (let i = 0; i < shortlistedIDs.length; i++) {      
    var rumour = rumours[shortlistedIDs[i]]; // Find the entry of the rumour

    // If a rumour in the set is present in the shortlist, add it to the question
    if (rumour != null) { shortlist.push(rumour) }
  }

  return shortlist
}

/**
 * Move given id to the Forms folder in the shared drive
 */
function moveFile(id) {
  var file = DriveApp.getFileById(id)
  var annotationFolder = getAnnotationFolder()
  var formFolder = annotationFolder.getFoldersByName("Forms").next()

  file.moveTo(formFolder)
}

/**
 * Returns the annotation root folder in the shared drive
 * @return {DriveApp.Folder}
 */
function getAnnotationFolder() {
  var sharedDriveID = "0AIwfpJgb62NvUk9PVA"
  var sharedDriveFolder = DriveApp.getFolderById(Drive.Drives.get(sharedDriveID).id)  
  return sharedDriveFolder.getFoldersByName("Annotation").next()
}

/**
 * Write a record of the created form and response sheet
 * @param {FormApp.Form} form
 */
function writeFormLog(form, name) {
  var id = form.getId()
  var url = form.getPublishedUrl()
  var destID = form.getDestinationId()
  var responseSheet = SpreadsheetApp.openById(destID)
  var responseURL = responseSheet.getUrl()

  // Write to sheet

  // Get spreadsheet
  var annotationFolder = getAnnotationFolder()
  var sheetID = annotationFolder.getFilesByName("FormIDs").next().getId()
  var spreadsheet = SpreadsheetApp.openById(sheetID)

  var datetime = new Date().toUTCString()

  spreadsheet.appendRow([datetime, id, name, url, responseURL])
}

/**
 * Exercise the generateAnnotationForm function
 */
function testGenerateForm() {
  var name = "Annotation Test Form"

  var tweetJSON = JSON.stringify(
    { 
      tweetSample: [
        { 
          tweetID: 'gioshwsejh32hg39', 
          text: 'covid is not as bad as normal flu #plandemic',
          rumourShortlist: [ '001', '008', '016', '080' ]
        },
        {
          tweetID: 'q1tusehjsehj9oi3g23', 
          text: '@user drinking bleach cures covid',
          rumourShortlist: [ '015', '008', '100', '211' ]
        }
      ]
    }
  )

  var rumourJSON = JSON.stringify(
    { 
      '001': {category: 'VACCINE', veracity: true, description: 'Vaccines cause autism.'},
      '008': {category: 'MEDICAL', veracity: false, description: 'Drink lots of water and you will be fine.'},
      '015': {category: '5G', veracity: false, description: '5G towers contribute to the spread of Coronavirus'}      
    }
  )

  Logger.log(tweetJSON)
  Logger.log(rumourJSON)

  generateAnnotationForm(name, tweetJSON, rumourJSON)
}
