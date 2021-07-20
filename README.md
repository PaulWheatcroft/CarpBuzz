<img src="static/images/smartmockup-cb.png" style="margin: 0;">

# Carp Buzz
<img src="static/images/cb-small.png" style="margin: 0;">

>
> Carp Buzz is a directory of fisheries in the South West of England.
>

The live site has been deployed to https://carp-buzz-dev.herokuapp.com/

<!-- TOC -->

- [Carp Buzz](#carp-buzz)
    - [User Experience UX](#user-experience-ux)
        - [User Stories](#user-stories)
- [Wireframing](#wireframing)
    - [Website Architecture](#website-architecture)
        - [Database](#database)
        - [Application](#application)
        - [Frontend](#frontend)
        - [Security](#security)
    - [Design Choices](#design-choices)
    - [Technologies](#technologies)
        - [Languages Used](#languages-used)
        - [Frameworks, Libraries, Databases & Programs Used](#frameworks-libraries-databases--programs-used)
    - [Testing](#testing)
        - [Testing User Stories from User Experience UX Section](#testing-user-stories-from-user-experience-ux-section)
            - [All Users](#all-users)
            - [Registered Users](#registered-users)
            - [Administrator](#administrator)
    - [Deployment](#deployment)
    - [Bugs and issues](#bugs-and-issues)
    - [Future development](#future-development)
    - [Acknowledgements](#acknowledgements)
    - [Further Development Ideas](#further-development-ideas)

<!-- /TOC -->

## User Experience (UX)

### User Stories

Working with the founder of Carp Buzz the following personas and user stories have been identified:

>
> All Users
>

- As someone who wants to go carp fishing, I can easily view a directory of fisheries in the South West of England
- As someone who wants to go carp fishing, I can filter a directory of fisheries in the South West of England based on location
- As someone who wants to go carp fishing, I can view any reviews a fishery has
- As someone who wants to go carp fishing, if I read a review that  has questionable or offensive text I can report the review to the website administrator
- As someone who wants to go carp fishing, I can view any catch reports a fishery has
- As someone who wants to go carp fishing, if I have any questions or queries and can send a message to Carp Buzz

>
> Registered Users
>
- As someone who has been carp fishing and who is registered to the site, I can leave a review of a fishery that I visited
    - I can edit my reviews at a later date
    - I can delete my reviews
- As someone who is currently carp fishing and who is registered to the site, I can log the fish I catch on my fishing trip
    - I can easily add fish individually as I catch them
    - I can view this report at a later date
    - I can amend this report at a later date
    - I can delete my reports

>
> Administrator
>
- As an administrator of the site, I can add new fisheries to the directory
- As an administrator of the site, I can amend existing fishery entries
- As an administrator of the site, I can delete fisheries from the directory
- An administrator of the site, I can moderate fishery reviews when notified by someone who uses the “report review” function.
    - I can deleted the review
    - I can remove the review from moderation should it be OK to do so
- As an administrator of the site, I can view any messages that have been sent using a contact form

These user stories helped inform a feature backlog that is kept in [Trello](https://trello.com/b/xP7HGN7D/carp-buzz). This also informed what the minimum viable product was for the project.


# Wireframing

<img src="static/images/cb-wireframe.png" style="margin: 0;width:500px">

Mocking up of the site was done using Figma collaborating with Carp Buzz founder Ben Hesketh.

The features outlined in the MVP were used to shape the wireframe images. After review it was decided to keep the filter option on the main fisheries view to just the county the fishery is located in as this presented a cleaner interface.

[Figma Wireframes](https://www.figma.com/file/3G7nX6FtgMuFxYMjBPjuQc/Carp-Buzz?node-id=0%3A1)


## Website Architecture

### Database

Data for Carp Buzz is stored in a MongoDB document database called carp+buzz.
<img src="static/images/cb-data.png" style="margin: 0;">

This database is segregated in to 9 collections.

- fisheries.contact
- fisheries.facilities
- fisheries.payment
- fisheries.tickets
- accounts
- reviews
- catch.reports
- catch.fish
- messages

The fisheries collection is broken down in to the 4 sub-collection you see above following best practice. The fisheries.contact can be considered as the primary collection as the individual documents generate the ID that links the the other subcollections. This fishery ID is also used to link the reviews collection and both of the catch collections.

When a fishery is deleted by an administrator the fisheries.facilities, fisheries.payment and fisheries.tickets are removed whilst fisheries.contact is given a hidden value and remains in the collections. This keeps the integrity of the catch.report and catch.fish data.

The catch collection is divided in 2 so that fish caught are indivually recorded making further enhancements using the data possible such as returning fish date georaphically or returning information based on type or size.

https://lucid.app/lucidchart/invitations/accept/inv_7b410190-ce33-47a5-80bd-387f7c72f0c6

### Application

The application is build on the [Flask](https://flask.palletsprojects.com/en/2.0.x/) framework and uses Python to interface with MongoDB and to present data to the frontend.
### Frontend

As the site is built upon the Flask framework the application is reliant on the [Jinja](https://jinja.palletsprojects.com/en/3.0.x/) templating language and is designed to be a single page application. This means individual pages do not need to be re-loaded in order to view updated content.

To render the card layout shown in the wireframes MaterializeCSS was chosen for the structural framwork for the HTML and CSS code.

### Security

Security is provided through the [Werkzeug](https://werkzeug.palletsprojects.com/en/2.0.x/) application library. This facilitates specific identity access management to features and pages. These specific account requirements are implemented both on the UI and at the python function level.

## Design Choices

The website has been built as a mobile first site.

The Materialize side-nav was chosen to enahance the mobile experience. The word menu was chosen above using the burger icon for usability purposes.

The h1 and h2 heading and Carp Buzz font was changed from 'Questrial' to 'Otomanopee One' to give a less corporate feel following feedback from users.

Below is the brand colour pallet for Carp Buzz. A complimentary colour pallet was used in relation to the brand colors.

| Description | Hex Colour Value |
| --- | ----------- |
| Carp Buzz primary Colour Blue  | #689DA8 |
| Carp Buzz secondary colour green | ##89A857 |
| Off white used for backgrounds or light text | #f7f7f7 |
| Dark grey primarily used for font color | #383838 |

The Carp Buzz logo was removed from the menu bar as it overcomplicated the look of the navigation.

The card to display fishery information was designed to host a significant amount of information. Having the expandable element helped keep this view clear without taking up too much screen height per fishery.

Bold Materialize colours were used for the functional buttons on the app to help usability.

## Technologies

### Languages Used

- [HTML5](https://en.wikipedia.org/wiki/HTML5): Is used to structure the website
- [CSS3](https://en.wikipedia.org/wiki/CSS): Is used for the sytling of the site
- [Python](https://www.python.org/): Is used to program the functionality of the application
- [Jinja template language](https://jinja.palletsprojects.com/en/3.0.x/) Is used to render the data passed to it to the DOM
- [Jquery](https://jquery.com/): Is used to nitialise several Materialize CSS components

### Frameworks, Libraries, Databases & Programs Used

- [Flask](https://flask.palletsprojects.com/en/2.0.x/): Flask is used as a programming framework 
- [Materialize](https://materializecss.com/): CSS framework used to speed up design, layout and build of the website 
- [Werkzeug](https://werkzeug.palletsprojects.com/en/2.0.x/): Is used for the security elements of Identity Access Management
- [Google Fonts](https://fonts.google.com/): Google fonts were used to import the 'Otomanopee One' and 'Questrial' fonts
- [Font Awesome](https://fontawesome.com/): Font Awesome was used for any icons
- [Git](https://git-scm.com/): Git was used for version control by utilizing the Gitpod terminal to commit to Git and Push to GitHub
- [Gitpod](https://www.gitpod.io/): Gitpod was used as the initial development environment
- [Microsoft VS Code](https://code.visualstudio.com/) Was used after the application development was started in GitPod after the monthly time usage had expired
- [GitHub](https://github.com/): GitHub is used to store the projects code after being pushed from Git
- [Figma](https://www.figma.com/): Figma was used to create the wireframes during the design process

## Testing

A code review was posted in the Code Institute peer-code-review channel.

A number of people I know carried out user testing. This resulted in a number of bugs found and fixed and usability improvements.

Functional testing was carried out against every element to ensure everything worked and was linked as expected before user tested was started. This was recorded in [functional-testing.xlsx](functional-testing.xlsx). Another tab was added after user testing to regression test functionality following changes through the user testing feedback.### Validation
Python code was tested for PEP8 compliancy with no issues http://pep8online.com
HTML was tested though https://validator.w3.org/ by copying and pasting in the page source for each page. This raised on error that I've accepted.
Accepted error:
<img src="static/images/accepted-error.png" style="margin: 0;">
Each error is generated from a select element that does have a unique id. Therefore it is not a muliple selection is a single selection element.

### Testing User Stories from User Experience (UX) Section

#### All Users
>
> As someone who wants to go carp fishing
>
- I can easily view a directory of fisheries in the South West of England
    1. Upon landing on the website the user is presented with 
- I can filter a directory of fisheries in the South West of England based on location
- I can view any reviews a fishery has
- if I read a review that  has questionable or offensive text I can report the review to the website administrator
- I can view any catch reports a fishery has
- if I have any questions or queries and can send a message to Carp Buzz
#### Registered Users
>
> As someone who has been carp fishing and who is registered to the site
>
- I can leave a review of a fishery that I visited
- I can edit my reviews at a later date
- I can delete my reviews
>
> As someone who is currently carp fishing and who is registered to the site
>
- I can log the fish I catch on my fishing trip
- I can easily add fish individually as I catch them
- I can view this report at a later date
- I can amend this report at a later date
- I can delete my reports

#### Administrator
>
>As an administrator of the site
>
- I can add new fisheries to the directory
- I can amend existing fishery entries
- I can delete fisheries from the directory
- I can moderate fishery reviews when notified by someone who uses the “report review” function.
- I can deleted the review
- I can remove the review from moderation should it be OK to do so
- As an administrator of the site, I can view any messages that have been sent using a contact form


## Deployment


## Bugs and issues

## Future development

## Acknowledgements

The project was started using the The Code Institute's [Gitpod Full Template](https://github.com/Code-Institute-Org/gitpod-full-template).

Border https://www.steckinsights.com/shorten-length-border-bottom-pure-css/ 

Cancelling of flash messages https://stackoverflow.com/questions/57660542/flask-closing-flash-message

https://smartmockups.com/ was used for the image in the README


## Further Development Ideas

