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
function generateAnnotationForm(formName, tweetsToAnnotate, knownRumours, metaData) {
  // Check that JSONS are formatted correctly
  if (badlyFormattedParameters(formName, tweetsToAnnotate, knownRumours)) {
    return "Check that the fields are filled out and the JSON strings are structured correctly!"
  }

  var description = "This form contains a set of social media posts, ready for annotation. " +
                    "You will be asked to determine which category a tweet belongs to, " +
                    "and which COVID-19 claim it discusses."

  try {

    // Create form with title
    var form = FormApp.create(formName)
      .setTitle(formName)
      .setDescription(description)
      .setCollectEmail(false)
      .setProgressBar(true)
      .setLimitOneResponsePerUser(true)
      .setAllowResponseEdits(true)
      .setRequireLogin(false)
      .setPublishingSummary(true)

    // Create spreadsheet destination
    var destination = SpreadsheetApp.create(formName + "_" + form.getId() + "_responses")
    form.setDestination(FormApp.DestinationType.SPREADSHEET, destination.getId())

    // move to shared drive folder
    moveFile(form.getId())    
    moveFile(destination.getId())

    writeFormLog(form, formName, metaData) // write ID and URLs to sheet


    // ~~~ CONSTRUCT QUESTIONS ~~~ //

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

    // Parse JSON strings
    var tweets = JSON.parse(tweetsToAnnotate).tweetSample
    knownRumours = knownRumours.replace('\t', ' ') // Replace tab characters, so later they don't interfere when downloading TSV
    var rumours = JSON.parse(knownRumours)

    // Write Tweet IDs to destination spreadsheet
    // writeResponseColumnHeaders(destination, tweets)

    // ~~~ NEW PAGE FOR EACH TWEET ~~~ //

    // For each tweet, create a new annotation question
    for (let i = 0; i < tweets.length; i++) {
      var tweet = tweets[i]

      // New page
      form.addPageBreakItem()
        .setTitle("Tweet #" + tweet.numericID)

      // ~~~ Category annotation ~~~ //

      var categoryHeader = form.addSectionHeaderItem()
      categoryHeader.setTitle(tweet.text)

      var categoryQuestion = form.addMultipleChoiceItem();
      categoryQuestion.setTitle("Tweet #" + tweet.numericID + ": Category")
      categoryQuestion.setHelpText("Which category does this Tweet primarily belong to?")

      var categories = [
        "Public Authority",
        "Community",
        "Medical Advice",
        "Prominent Actors",
        "Conspiracy",
        "Virus Transmission",
        "Virus Origin",
        "Civil Unrest",
        "Vaccine",
        "Other"
      ]

      categoryQuestion.setChoiceValues(categories);

      // ~~~ Rumour identification ~~~ //      

      var rumourHeader = form.addSectionHeaderItem()
      rumourHeader.setTitle(tweet.text)

      var rumourQuestion = form.addMultipleChoiceItem();      
      rumourQuestion.setTitle("Tweet #" + tweet.numericID + ": Claim Identification")
      rumourQuestion.setHelpText("Which claim does this Tweet primarily discuss?")

      // Get rumour shortlist
      // ToDo: Filter rumour shortlist based on annotated category?
      var shortlistedRumours = parseShortlist(tweet, rumours)

      // Add rumour descriptions as response choices
      var choices = shortlistedRumours.map(r => { return "Claim #" + r.rumourID + ": " + r.description })
      choices.push('Other: Claim not listed')
      choices.push('Other: Does not discuss a claim')

      rumourQuestion.setChoiceValues(choices)
    }
  }
  catch (error) {
    Logger.log(error)
    return error.toString()
  }

  Logger.log('Published URL: ' + form.getPublishedUrl())
  Logger.log('Editor URL: ' + form.getEditUrl())

  return 'Success! <a href=' + form.getPublishedUrl() + ' target="_blank">View Generated Form</a>'
}

/**
 * DOESN'T SEEM TO OVERWRITE HEADER CORRECTLY. JUST SOLVE IN PARSER?
 * Overwrite the question title with info more useful for parsing
 * @param {SpreadsheetApp.Spreadsheet} destination
 * @param {Object[]} tweets
 * 
function writeResponseColumnHeaders(destination, tweets) {
  var tweetIDs = tweets.map(tweet => { return tweet.tweetID })
  var columnHeaders = []
  for (let i = 0; i < tweetIDs.length; i++) {
    columnHeaders.push("category " + tweetIDs[i])
    columnHeaders.push("claim " + tweetIDs[i])
  }

  destination.getSheetByName("Form Responses 1").getRange(2, 4, 1, columnHeaders.length)
    .setValues([columnHeaders])
}
*/

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
    JSON.parse(knownRumours)    
    var tweetsJSON = JSON.parse(tweetsToAnnotate)
    
    // Check tweet array is defined
    var tweets = tweetsJSON.tweetSample
    if (tweets == null || tweets == undefined) {
      // Tweets to Annotate doesn't contain a root "tweetSample" property!
      return true
    }
  }
  catch (ex) {
    // Something went wrong!
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
    var rumourIDString = shortlistedIDs[i].toString()  
    var rumour = rumours[rumourIDString]; // Find the entry of the rumour

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
function writeFormLog(form, name, metaData) {
  var id = form.getId()
  var url = form.getPublishedUrl()
  var destID = form.getDestinationId()
  var responseSheet = SpreadsheetApp.openById(destID)
  var responseURL = responseSheet.getUrl()

  // Write to sheet

  // Get spreadsheet
  var annotationFolder = getAnnotationFolder()
  var sheetID = annotationFolder.getFilesByName("Forms Record").next().getId()
  var spreadsheet = SpreadsheetApp.openById(sheetID)

  var datetime = new Date().toUTCString()

  spreadsheet.appendRow([datetime, id, name, url, responseURL, metaData])
}

/**
 * Exercise the generateAnnotationForm function
 */
function testGenerateForm() {
  var name = "Annotation Test Form"
  var metaData = ""

  var tweetJSON = JSON.stringify(
    { 
      tweetSample: [
        { 
          tweetID: 'gioshwsejh32hg39',
          numericID: 1,
          text: 'covid is not as bad as normal flu #plandemic',
          rumourShortlist: [ 1, 8, 16, 80 ]
        },
        {
          tweetID: 'q1tusehjsehj9oi3g23', 
          numericID: 2,
          text: '@user drinking bleach cures covid',
          rumourShortlist: [ 15, 8, 100, 211 ]
        }
      ]
    }
  )

  var rumourJSON = JSON.stringify(
    { 
      '1': {rumourID: 1, category: 'VACCINE', veracity: "FALSE", description: 'Vaccines cause autism.'},
      '8': {rumourID: 8, category: 'MEDICAL', veracity: "FALSE", description: 'Drink  lots of water and you will be fine.'},
      '15': {rumourID: 15, category: '5G', veracity: "FALSE", description: '5G towers\tcontribute to the spread of Coronavirus'}      
    }
  )

  Logger.log(tweetJSON)
  Logger.log(rumourJSON)

  var response = generateAnnotationForm(name, tweetJSON, rumourJSON, metaData)
  Logger.log(response)
}
