"""Stores the documents collected by the oplog workers. 

It is meant as an intermediate layer that hides the details of sharding 
and provides an API for backends like Solr/Sphinx/etc to use to gather 
documents. 
"""
#!/usr/env/python
import sys

from pysolr import Solr
from threading import Timer
from util import verify_url, retry_until_ok

class SolrDocManager():
    """The DocManager class contains a dictionary that stores id/doc pairs. 

    The reason for storing id/doc pairs as opposed to doc's is so that multiple 
    updates to the same doc reflect the most up to date version as opposed to 
    multiple, slightly different versions of a doc.                                                                           
    """
    
    def __init__(self, url, auto_commit = True):
        """Just create a dict
        """
	if verify_url(url) is False:
		print 'Invalid Solr URL'
		return None	

        self.solr = Solr(url)   
	if auto_commit:
        	self.solr_commit()          


    def upsert(self, docs):
        """Update or insert documents into Solr
        """
        self.solr.add(docs, commit=False)
        
    def remove(self, doc_id):
        """Removes documents from Solr
        """
        self.solr.delete(id=str(doc_id), commit=False)
        
    def search(self, query):
        """Called by oplog_manager to query Solr
        """
        return self.solr.search(query)
    
    
    def commit(self):
        retry_until_ok(self.solr.commit)

    def solr_commit(self):
        """Periodically commits to the Solr server.
        """ 
        self.solr.commit()
        Timer(1, self.solr_commit).start() 
        
    def get_last_doc(self):
        """Returns the last document stored in the Solr engine.
        """
        #search everything, sort by descending timestamp, return 1 row
        result = self.solr.search('*:*', sort='_ts desc', rows=1)
        
        if len(result) == 0:
            return None
            
        return result.docs[0]
            
    
            

        
    
        
        
    
    
    
