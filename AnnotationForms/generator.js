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

  try {
    // Create form, response sheet, move to Shared Drive folder, and write record log
    var form = createFormAndResponses(formName, metaData)

    createParticipantNumQuestion(form)

    var tweets = parseJSON(tweetsToAnnotate).tweetSample
    var rumours = parseJSON(knownRumours)

    // Create all pages and questions first
    var pages = createFormPages(form, tweets)

    // Create hidden metadata page
    var submitPage = createMetaDataPage(form, tweets, rumours)

    for (let i = 0; i < pages.length; i++) {
      // Now set the choices for each question to navigate to the correct page
      var categoryQuestion = pages[i].question

      // Create a choice for each category, which navigates to the claim page for that category
      categoryQuestion.setChoices(pages[i].claimPages.map(claimPage => {
        return categoryQuestion.createChoice(claimPage.category, claimPage.page)
      }))

      // For each claim page
      for (let j = 0; j < pages[i].claimPages.length; j++) {
        var claimPage = pages[i].claimPages[j]

        // Skip to next tweet page or end of form if no more tweets!
        var navigatePage = (i < pages.length - 1) ? pages[i+1].page : submitPage
        claimPage.page.setGoToPage(navigatePage)

        // Create claim shortlists
        // ToDo: Filter by category
        var shortlist = parseShortlist(pages[i].tweet, rumours, claimPage.category)
        var choices = shortlist.map(r => { return "Claim #" + r.rumourID + ": " + r.description })
        choices.push('Other: Claim not listed')
        choices.push('Other: Does not discuss a claim')

        claimPage.question.setChoiceValues(choices)
      }
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
 * 
 */
function createFormAndResponses(formName, metaData) {
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
  moveFile(form.getId(), 'Forms')    
  moveFile(destination.getId(), 'Responses')

  writeFormLog(form, formName, metaData) // write ID and URLs to sheet

  return form
}

/**
 * Creates participant number question with numeric validation and adds to form
 */
function createParticipantNumQuestion(form) {
  // For numeric answer questions
    var numericValidation = FormApp.createTextValidation()
      .setHelpText('Input must be a number between 0 and 100.')
      .requireNumberBetween(0, 100)
      .build()
    
    // Participant ID number
    return form.addTextItem()
      .setTitle('Participant ID')
      .setHelpText('Your unique participant number, provided when you signed up for the study.')
      .setRequired(true)
      .setValidation(numericValidation)
}

/** Data structure containing all the pages of the form
 * @return {array}
 * [ // for each tweet
 *  { tweet: tweet, page: annotateCategoryPage, claimPages: [ {category: string, page: page } ] }
 * ]
 */
function createFormPages(form, tweets) {
  var pages = []

  // For each tweet, create a new annotation question
  for (let i = 0; i < tweets.length; i++) {
    var categoryPage = form.addPageBreakItem()
      .setTitle("Tweet #" + (i+1))

    // Tweet text
    form.addSectionHeaderItem()
      .setTitle(tweets[i].text)
    
    // Annotate category
    var categoryQuestion = form.addMultipleChoiceItem();
    categoryQuestion.setTitle("Tweet #" + (i+1) + ": Category")
    categoryQuestion.setHelpText("Which category does this Tweet primarily belong to?")

    // For each category, present claim shortlist
    var claimPages = categories.map(category => {
      var claimPage = form.addPageBreakItem()
      claimPage.setTitle("Claim Identification")
      
      // Tweet text
      form.addSectionHeaderItem()
        .setTitle(tweets[i].text)

      // Annotate claim
      var claimQuestion = form.addMultipleChoiceItem()
      claimQuestion.setTitle("Claims: " + category)
      claimQuestion.setHelpText("Which claim does this Tweet primarily discuss?")

      return {"category": category, "page": claimPage, "question": claimQuestion} 
    })
    
    // Populate data structure
    pages.push({
      "tweet": tweets[i], 
      "page": categoryPage, 
      "question": categoryQuestion, 
      "claimPages": claimPages
    })
  }

  return pages
}

/**
 * 
 */
function createMetaDataPage(form, tweets, rumours) {
  // Submit page
  var submitPage = form.addPageBreakItem()
  submitPage.setTitle("Submit")
  submitPage.setHelpText("Thank you for your time! We are always in need of more data to improve the quality of our research, so please contact the research team if you would like to annotate more tweets.")
  submitPage.setGoToPage(FormApp.PageNavigationType.SUBMIT) // Skip the metadata page

  form.addPageBreakItem()
    .setTitle("Invisible Page - Ignore!")
    .setGoToPage(FormApp.PageNavigationType.SUBMIT)
  
  form.addTextItem()
    .setTitle(JSON.stringify(tweets))

  form.addTextItem()
    .setTitle(JSON.stringify(rumours))
  
  return submitPage
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
 * Return a list of rumours for the given tweet, filtered by category
 */
function parseShortlist(tweet, rumours, category) {
  var shortlist = []

  // For each rumour in the shortlist...
  var shortlistedIDs = tweet.rumourShortlist
  for (let i = 0; i < shortlistedIDs.length; i++) {    
    var rumourIDString = shortlistedIDs[i].toString()  
    var rumour = rumours[rumourIDString]; // Find the entry of the rumour

    // Add if rumour exists and matches the category
    if (rumour != null && rumour.category == category) { shortlist.push(rumour) }
  }

  return shortlist
}

/**
 * Move given id to the Forms folder in the shared drive
 */
function moveFile(id, subdirectory) {
  var file = DriveApp.getFileById(id)
  var annotationFolder = getAnnotationFolder()
  var folder = annotationFolder.getFoldersByName(subdirectory).next()

  file.moveTo(folder)
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
          text: 'covid is not as bad as normal flu #plandemic',
          rumourShortlist: [ 1, 8, 16, 80 ]
        },
        {
          tweetID: 'q1tusehjsehj9oi3g23',
          text: '@user drinking bleach cures covid',
          rumourShortlist: [ 15, 8, 100, 211 ]
        }
      ]
    }
  )

  var rumourJSON = JSON.stringify(
    { 
      '1': {rumourID: 1, category: 'Virus origin and properties', veracity: "FALSE", description: 'Vaccines cause autism.'},
      '8': {rumourID: 8, category: 'Medical advice and self-treatments', veracity: "FALSE", description: 'Drink  lots of water and you will be fine.'},
      '15': {rumourID: 15, category: 'Conspiracy theories', veracity: "FALSE", description: '5G towers contribute to the spread of Coronavirus'}      
    }
  )

  Logger.log(tweetJSON)
  Logger.log(rumourJSON)

  var response = generateAnnotationForm(name, tweetJSON, rumourJSON, metaData)
  Logger.log(response)
}
