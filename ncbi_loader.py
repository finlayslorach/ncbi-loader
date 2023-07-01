from llama_index.readers.base import BaseReader
from llama_index.readers.schema.base import Document
from typing import Optional
import xml.etree.ElementTree as xml
from Bio import Entrez
from Bio import SeqIO
import time


Entrez.email='finlayslorach@gmail.com'

# Query 
class NcbiReader(BaseReader):
    """
        Returns the top document for a given search query of a gene sequence
    """

    def load_data(
        self, 
        search_term: str,
        max_results: Optional[int] =  1) -> Document:
        
        handle = Entrez.esearch(db='nucleotide', term=search_term, retmax=max_results)
        record = handle.read()
    
        root = xml.fromstring(record)

        for elem in root.iter():
    
            if elem.tag == 'Id':
                
                _id = elem.text

                # Fetch fasta file for each id fetched // assume first fetch is most relevant???
                complete_document = []
                
                try: 
                    # Fetch the record 
                    handle = Entrez.efetch(db='nucleotide', id=_id, rettype='gb')
                    record = handle.read()
                    handle.close()

                    # Parse genbank file 
                    filename = f'{_id}.gb'
                    out_handle = open(filename, 'w')
                    out_handle.write(record.rstrip('\n'))

                    genbank_obj = SeqIO.read(filename, 'genbank')
                    time.sleep(1)
                
                except Exception as e:
                    print('Unable to fetch gene or it does not exist')
                    pass

                # Compile document for chatGPT
                complete_document = Document(

                    genbank_obj.seq,

                    extra_info={
                        'description': genbank_obj.description,
                        'id': genbank_obj.id,
                        'name': genbank_obj.name,
                        'reverse_complement': genbank_obj.reverse_complement,
                        'features': genbank_obj.features,
                    }
                )
        return complete_document
    




















