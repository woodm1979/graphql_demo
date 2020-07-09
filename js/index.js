const { v4: uuidv4 } = require('uuid')

const { ApolloServer, gql } = require('apollo-server');

recipesTable = [
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

usersTable = [
  {
    'id': "e2b23275-3a78-448a-b4c8-8e1c82e4344d",  // This will be "me"
    'firstName': 'Samantha',
    'lastName': 'Stevenson',
    'recipeIds': [
      recipesTable[0]['id'],
      recipesTable[1]['id'],
    ],
  },
  {
    'id': "45f82425-2796-4b6a-9db4-b484d9512605",
    'firstName': 'James',
    'lastName': 'Jones',
    'recipeIds': [
      recipesTable[2]['id'],
      recipesTable[3]['id'],
    ],
  },
  {
    'id': "593dedc5-e22e-482d-a17a-9d350b664abe",
    'firstName': 'Pat',
    'lastName': 'Peterson',
    'recipeIds': [
      recipesTable[1]['id'],
      recipesTable[2]['id'],
      recipesTable[3]['id'],
    ],
  },
]


// Fetchers
const getAllUserIds = () => usersTable.map(user => user.id)

const getUserById = (id) => {
  console.log(`==========> Fetching user: ${id}`)
  return usersTable.find(user => user.id === id);
}

const getManyUsersById = (ids) => ids.map(getUserById)


// Queries

const typeDefs = gql`
  type Query {
    hello(name: String!): String
    users(id: ID): [User]
    recipes: [Recipe]
    me: User
  }

  type User {
    id: ID
    firstName: String
    lastName: String
    recipes: [Recipe]
  }

  type Recipe {
    id: ID
    name: String
    users: [User]
  }
  
  type AddRecipe {
    ok: Boolean
    recipe: Recipe
  }
  
  type Mutation {
    addRecipe(name: String): AddRecipe
  }
`

const resolvers = {
  Query: {
    hello: (parent, args, context) => (`Hello ${args.name}`),
    users: (parent, args, context) => {
      let ids = getAllUserIds()
      if (args.id) {
        ids = [args.id]
      }
      return getManyUsersById(ids)
    },
    recipes: (parent, args, context) => [...recipesTable],
    me: (parent, args, context) => {
      return getUserById(context.userId)
    },
  },
  User: {
    recipes: (parent, args, context) => {
      return recipesTable.filter(recipe => parent.recipeIds.includes(recipe.id))
    },
  },
  Recipe: {
    users: (parent, args, context) => {
      const userIds = usersTable.map(user => {
        if (user.recipeIds.includes(parent.id)) {
          return user.id
        }
      }).filter(Boolean)
      return getManyUsersById(userIds)
    },
  },
  Mutation: {
    addRecipe: (parent, args, context) => {
      let ok = true
      // TODO: Handle errors here.
      const recipe = {
        id: uuidv4(),
        name: args.name,
      }
      recipesTable.push(recipe)
      return {
        ok,
        recipe,
      }
    },
  },
}


// Setup the server

const getLoggedInUserId = ({req}) => {
  // Do JWT processing and database lookups and ... here.
  return {userId: "e2b23275-3a78-448a-b4c8-8e1c82e4344d"}
}

const server = new ApolloServer({
  typeDefs,
  resolvers,
  context: getLoggedInUserId
});

// The `listen` method launches a web server.
server.listen().then(({ url }) => {
  console.log(`🚀  Server ready at ${url}`);
});
