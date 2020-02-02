#!/bin/bash

echo "Show all created persons: "
curl -X GET localhost:5000/persons

curl -X DELETE localhost:5000/persons

echo "Show all created persons: "
curl -X GET localhost:5000/persons