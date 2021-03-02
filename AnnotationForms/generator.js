

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

  // Parse JSON strings
  var tweets = JSON.parse(tweetsToAnnotate).tweetSample
  var rumours = JSON.parse(knownRumours)

  var description = "Please annotate the following tweets."

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

  // For numeric answer questions
  var numericValidation = FormApp.createTextValidation()
    .setHelpText('Input must be a number between 0 and 100.')
    .requireNumberBetween(0, 100)
    .build();
  
  // Participant ID number
  var participantNumberQ = form.addTextItem()
    .setTitle('Participant ID')
    .setHelpText('Your unique participant number, provided when you signed up for the study.')
    .setRequired(true)
    .setValidation(numericValidation)

  // For each tweet, create a new annotation question
  for (let i = 0; i < tweets.length; i++) {
    var tweet = tweets[i]
    var question = form.addMultipleChoiceItem();
    
    question.setTitle('Which rumour does this tweet discuss?')
    question.setHelpText(tweet.text)

    // Get rumour shortlist
    var shortlistedRumours = parseShortlist(tweet, rumours)

    // Add text descriptions to question
    question.setChoiceValues(shortlistedRumours.map(r => { return r.description }))

    // Allow 'other' response
    question.showOtherOption(true)

  }

  Logger.log('Published URL: ' + form.getPublishedUrl())
  Logger.log('Editor URL: ' + form.getEditUrl())
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
      '001': {category: 'VACCINE', veracity: true, description: '...'},
      '008': {category: 'MEDICAL', veracity: false, description: '...'},
      '015': {category: '5G', veracity: false, description: '...'}      
    }
  )

  generateAnnotationForm(name, tweetJSON, rumourJSON)
}
