## Fast-Food-Fast

Fast-Food-Fast is a food delivery service app for a restaurant.

[![Build Status](https://travis-ci.com/mubstimor/fast-food-fast.svg?branch=api)](https://travis-ci.com/mubstimor/fast-food-fast)  [![Coverage Status](https://coveralls.io/repos/github/mubstimor/fast-food-fast/badge.svg?branch=api&service=github)](https://coveralls.io/github/mubstimor/fast-food-fast?branch=api&service=github)  [![Code Climate](https://codeclimate.com/github/codeclimate/codeclimate/badges/gpa.svg)](https://codeclimate.com/github/mubstimor/fast-food-fast)  [![Test Coverage](https://api.codeclimate.com/v1/badges/24230611fce8192b6279/test_coverage)](https://codeclimate.com/github/mubstimor/fast-food-fast/test_coverage)

### Template Link

[Home Page](https://mubstimor.github.io/fast-food-fast/ui/index.html)

### Heroku Link

[API Home Page](https://tims-fast-food.herokuapp.com/)

## Supported Functionality
|      Endpoint   |  Functionality |
|:-------------:|------:|
| POST /auth/signup | Register a user |
| POST /auth/login | Login a user |
| POST /users/orders | Create an order |
| GET /users/orders| Get a user's order history|
| GET /orders | Get all orders - Admin |
| GET ​/​orders​/<orderId> |   Get a given order - Admin |
| PUT /​orders​/<orderId> |   Update order status - Admin |
| GET /menu| Display menu items|
| POST /menu | Add menu item - Admin |

## Installation Instructions

To install dependencies, run
```
pip install -r requirements.txt
```
Set up a local Postgresql database and add two environment variables DATABASE_URL, and DATABASE_TEST_URL, forexample
```
DATABASE_TEST_URL=postgres://username:password@localhost:5432/test_database
```

## Screenshots

Authenticate user
![Authenticate user](https://user-images.githubusercontent.com/2491780/46521573-aa1dfe80-c888-11e8-9e8b-0a40f158a299.png)

View Single Order
![View Single Order](https://user-images.githubusercontent.com/2491780/46521573-aa1dfe80-c888-11e8-9e8b-0a40f158a299.png)
