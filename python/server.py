#!/usr/bin/env python

import logging
import uuid

from flask import Flask, g
from flask_graphql import GraphQLView
import graphene
from graphql import GraphQLError

logging.basicConfig(level=logging.DEBUG)

# Fake Database

recipes_table = [
    {
        'id': "4f56d71c-0988-4dad-97b3-108266827c0c",
        'name': 'Chocolate Cake',
    },
    {
        'id': "c9f063f4-2121-4394-860c-ed939096390b",
        'name': 'Spaghetti',
    },
    {
        'id': "62320110-dde3-4068-8b47-2dda783bb3db",
        'name': 'Brownies',
    },
    {
        'id': "6b912110-3984-4384-a351-7f30595a638d",
        'name': 'Lasagna',
    },
]

users_table = [
    {
        'id': "e2b23275-3a78-448a-b4c8-8e1c82e4344d",  # This will be "me"
        'first_name': 'Samantha',
        'last_name': 'Stevenson',
        'recipe_ids': [
            recipes_table[0]['id'],
            recipes_table[1]['id'],
        ],
    },
    {
        'id': "45f82425-2796-4b6a-9db4-b484d9512605",
        'first_name': 'James',
        'last_name': 'Jones',
        'recipe_ids': [
            recipes_table[2]['id'],
            recipes_table[3]['id'],
        ],
    },
    {
        'id': "593dedc5-e22e-482d-a17a-9d350b664abe",
        'first_name': 'Pat',
        'last_name': 'Peterson',
        'recipe_ids': [
            recipes_table[1]['id'],
            recipes_table[2]['id'],
            recipes_table[3]['id'],
        ],
    },
]


# Fetchers
def get_all_user_ids():
    # This code would never even remotely exist in production.
    # Please forgive this crappy nonsense.
    # ... cuz demo.
    return [user['id'] for user in users_table]


def get_user_by_id(id):
    app.logger.info('==========> Fetching user: %s', id)
    users = [user for user in users_table if user['id'] == id]
    if not users:
        return None
    return users[0]


def get_many_users_by_id(ids):
    return [get_user_by_id(id) for id in ids]


# Queries

class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stranger"))
    users = graphene.List(lambda: User, id=graphene.Argument(graphene.String))
    recipes = graphene.List(lambda: Recipe, id=graphene.Argument(graphene.String))
    me = graphene.Field(lambda: User)

    @staticmethod
    def resolve_hello(parent, info, name):
        return "Hello " + name

    @staticmethod
    def resolve_users(parent, info, id=None):
        user_ids = [id] if id else get_all_user_ids()
        users = get_many_users_by_id(user_ids)
        return users

    @staticmethod
    def resolve_recipes(parent, info, id=None):
        recipes = recipes_table[:]
        if id:
            recipes = [recipe for recipe in recipes if recipe['id'] == id]
        return recipes

    @staticmethod
    def resolve_me(parent, info):
        user = get_user_by_id(info.context['user_id'])
        if not user:
            raise GraphQLError('User not logged in')
        return user


class User(graphene.ObjectType):
    id = graphene.NonNull(graphene.ID)
    first_name = graphene.NonNull(graphene.String)
    last_name = graphene.NonNull(graphene.String)
    recipes = graphene.List(lambda: Recipe)

    @staticmethod
    def resolve_id(parent, info):
        return parent['id']

    @staticmethod
    def resolve_first_name(parent, info):
        return parent['first_name']

    @staticmethod
    def resolve_last_name(parent, info):
        return parent['last_name']

    @staticmethod
    def resolve_recipes(parent, info):
        # recipes = filter(lambda r: r['id'] in parent['recipe_ids'], recipes_table)
        recipes = [recipe for recipe in recipes_table if recipe['id'] in parent['recipe_ids']]
        return recipes


class Recipe(graphene.ObjectType):
    id = graphene.NonNull(graphene.ID)
    name = graphene.String()
    users = graphene.List(lambda: User)

    @staticmethod
    def resolve_id(parent, info):
        return parent['id']

    @staticmethod
    def resolve_name(parent, info):
        return parent['name']

    @staticmethod
    def resolve_users(parent, info):
        user_ids = [user['id'] for user in users_table if parent['id'] in user['recipe_ids']]
        return get_many_users_by_id(user_ids)


# Mutations

class AddRecipe(graphene.Mutation):
    class Arguments:
        name = graphene.String()

    ok = graphene.Boolean()
    recipe = graphene.Field(Recipe)

    @staticmethod
    def mutate(root, info, name):
        ok = True
        try:
            recipe = {
                'id': uuid.uuid4(),
                'name': name,
            }
            recipes_table.append(recipe)
        except Exception:
            ok = False
            recipe = None
        return {'ok': ok, 'recipe': recipe}


class Mutations(graphene.ObjectType):
    add_recipe = AddRecipe.Field()


# Setup the server

schema = graphene.Schema(
    query=Query,
    mutation=Mutations,
)


def get_logged_in_user_id():
    # Here we'd process the request's JWT to find a user ID.
    # Verify that user exists in our system, and return the user's ID.
    return "e2b23275-3a78-448a-b4c8-8e1c82e4344d"


app = Flask(__name__)
app.add_url_rule('/', view_func=GraphQLView.as_view(
    'graphql',
    schema=schema,
    graphiql=True,
    get_context=lambda: {'user_id': get_logged_in_user_id()}
))
