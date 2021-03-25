var description = "This form contains a set of social media posts, ready for annotation. " +
                    "You will be asked to determine which category a tweet belongs to, " +
                    "and which COVID-19 claim it discusses."

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

/**
 * Clean out bad characters and return JSON Object
 */
function parseJSON(jsonString) {
  // Replace tab characters, so later they don't interfere when downloading TSV
    cleanedString = jsonString.replace('\t', ' ')
    return JSON.parse(cleanedString)
}