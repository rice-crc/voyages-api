# Project Structure

The project is built around a microservices model. It intends to farm out work to dedicated, containerized processes wherever possible. This document provides an overview of those services.

## Supporting Containers

The app is supported with some infrastructural containers built by Docker. Refer to the main Readme file for instructions on these.

### Voyages-MySQL

The Django app is configured to use a MySQL db backend, running on port 3306.

### Voyages-Adminer

In order to directly inspect the database (when this is necessary), we have installed an Adminer container running on port 8080.

### Voyages-Solr

This service is used to index entities in the database (Voyages, Enslaved People, Enslavers, and Blog Posts). Currently, it is only being used for the global search feature. However, it would make sense to use this to index documents at well (though full-text search always requires some tuning).

## Python Containers

These containers run python services in Flask or Django. The "main" API container runs a barebones Django web app, which the other processes essentially index the data from, in order to provide efficient use of these data (for instance, when aggregating to make data visualizations).

### Voyages-API (Django)

This is the Python Django project that manages the database, provides an admin interface for directly editing the data, and presents the data out via API views.

A core principle of the rearchitecture was that the ORM should be exposed so that the relational data could be searched on more or less arbitrarily. For instance, you should be able to search Enslaved People by the name of the ship they were transported on, and you should be able to search Voyages for the names of the Enslaved People transported on them.

For notes on API usage and maintainer notes, refer to the [API's readme](api/README.md)

### Voyages-Stats (Flask)

This container uses Pandas to build in-memory databases that can quickly produce json summary statistics that fit well into the plotly.js graphing library. Typically, these requests are about providing summary statistics using pandas functions like groupby.

Right now, we've only applied these statistical operations to the voyages endpoint. We need to have discussions about how we want to visualize numerical data related to people.

### Voyages-People-Networks (Flask)

This container uses NetworkX to map the numerous connections between people and voyages.

Its development grew out of the fact that the database had to be restructured in order to efficiently represent the *many* many-to-many relations we get in connecting people to people, people to voyages, and peoples' relations to voyages. It was evident that this structural change lent itself to a different representation of the data, even internally. That said, we are not ready to move the full dataset to a graph db, given that voyages should probably stay in a traditional relational db for the foreseeable future.

Its default behavior is to receive an ID for one of its core object classes (an enslaved person, an enslaver, or a voyage), and to return the node with that ID, its neighbors out two hops, and the associated edges.

### Voyages-Geo-Networks (Flask)

This container uses NetworkX to create essentially a routing system, and then runs every entity for each object class through that routing system, in order to cache, in Pandas, a large dataframe of the various edges and weights for each entity, so that these can be aggregated on, and splined appropriately based on the weights.