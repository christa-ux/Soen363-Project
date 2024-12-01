//query 1
// Find an artist by name
db.Artists.find({ name: "The Killers" })

//in compass, it's written this way: 
{ name: "The Killers" }

// query 2
//find the number of audiobooks that satisfy: artist_id=105
db.Audiobooks.countDocuments({ artist_id: 105 })

//in compass, it is written this way: 
[
    { 
      $match: { artist_id: 105 } 
    },
    { 
      $count: "total_audiobooks_narrated" 
    }
  ]



//query 3
// Find top 3 audiobook narrators by total number of books narrated
db.AudiobookArtists.find()
  .sort({ total_books: -1 })
  .limit(3)

//in compass
  [
    { 
      $sort: { total_books: -1 } 
    },
    { 
      $limit: 3 
    }
  ]

  //query 4:
  // Group audiobooks by narrator and count their narrations
db.Audiobooks.aggregate([
    { $group: {
        _id: "$artist_id",
        total_narrations: { $sum: 1 }
      }
    },
    { $sort: { total_narrations: -1 } },
    { $lookup: {
        from: "AudiobookArtists",
        localField: "_id",
        foreignField: "artist_id",
        as: "narrator_details"
      }
    }
  ])
  //in compass: 
    [
        {
          $group: {
            _id: "$artist_id",
            total_narrations: { $sum: 1 }
          }
        },
        {
          $sort: { total_narrations: -1 }
        }
      ]


//query 5: 


// Create an index on artist name
db.Artists.createIndex({ name: 1 })

// Explain the query to see performance
db.Artists.find({ name: "The Killers" }).explain("executionStats")



//in compass: 

[
    {
      $match: {
        $text: { 
          $search: "Cormac McCarthy western" 
        }
      }
    },
    {
      $sort: { 
        score: { $meta: "textScore" } 
      }
    }
  ]


//query 6: 
// Create a text index on audiobook description
db.Audiobooks.createIndex({ description: "text" })

// Perform full-text search
db.Audiobooks.find(
  { $text: { $search: "Cormac McCarthy western" } },
  { score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } })