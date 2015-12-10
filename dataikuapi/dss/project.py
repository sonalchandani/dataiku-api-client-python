from dataset import DSSDataset
from managedfolder import DSSManagedFolder
from job import DSSJob
from scenario import DSSScenario
from apiservice import DSSAPIService


class DSSProject(object):
    """
    A project on the DSS instance
    """
    def __init__(self, client, project_key):
       self.client = client
       self.project_key = project_key
       
    ########################################################
    # Project deletion
    ########################################################
    
    def delete(self):
        """
        Delete the project

        Note: this call requires an API key with admin rights
        """
        return self.client._perform_empty(
            "DELETE", "/projects/%s" % self.project_key)

    ########################################################
    # Project export
    ########################################################
    
    def get_export_stream(self):
        """
        Return a stream of the exported project

        Warning: this stream will monopolize the DSSClient until closed
        """
        return self.client._perform_raw(
            "GET", "/projects/%s/export" % self.project_key).raw

    def export_to_file(self, path):
        """
        Export the project to a file
        
        Args:
            path: the path of the file in which the exported project should be saved
        """
        with open(path, 'w') as f:
            export_stream = self.client._perform_raw(
                "GET", "/projects/%s/export" % self.project_key)
            for chunk in export_stream.iter_content(chunk_size=10000):
                if chunk:
                    f.write(chunk)
                    f.flush()

    ########################################################
    # Project infos
    ########################################################

    def get_metadata(self):
        """
        Get the metadata attached to this project. The metadata contains label, description
        checklists, tags and custom metadata of the project
        
        Returns:
            a dict object. For more information on available metadata, please see
            https://doc.dataiku.com/dss/api/latest
        """
        return self.client._perform_json(
            "GET", "/projects/%s/metadata" % self.project_key)

    def set_metadata(self, metadata):
        """
        Set the metadata on this project.
        
        Args:
            metadata: the new state of the metadata for the project. You should only set a metadata object 
            that has been retrieved using the get_metadata call.
        """
        return self.client._perform_empty(
            "PUT", "/projects/%s/metadata" % self.project_key, body = metadata)

    def get_permissions(self):
       """
       Get the permissions attached to this project

        Returns:
            a JSON object, containing the owner and the permissions, as a list of pairs of group name
            and permission type
       """
       return self.client._perform_json(
          "GET", "/projects/%s/permissions" % self.project_key)

    def set_permissions(self, permissions):
        """
        Set the permissions on this project
        
        Args:
            permissions: a JSON object of the same structure as the one returned by get_permissions call
        """
        return self.client._perform_empty(
            "PUT", "/projects/%s/permissions" % self.project_key, body = permissions)

    ########################################################
    # Datasets
    ########################################################

    def list_datasets(self):
        """
        List the datasets in this project
        
        Returns:
            the list of the datasets, each one as a JSON object
        """
        return self.client._perform_json(
            "GET", "/projects/%s/datasets/" % self.project_key)

    def get_dataset(self, dataset_name):
        """
        Get a handle to interact with a specific dataset
       
        Args:
            dataset_name: the name of the desired dataset
        
        Returns:
            A :class:`dataikuapi.dss.dataset.DSSDataset` dataset handle
        """
        return DSSDataset(self.client, self.project_key, dataset_name)

    def create_dataset(self, dataset_name, type,
                params={}, formatType=None, formatParams={}):
        """
        Create a new dataset in the project, and return a handle to interact with it
        
        Args:
            dataset_name: the name for the new dataset
            type: the type of the dataset
            params: the parameters for the type, as a JSON object
            formatType: an optional format to create the dataset with
            formatParams: the parameters to the format, as a JSON object
        
        Returns:
            A :class:`dataikuapi.dss.dataset.DSSDataset` dataset handle
        """
        obj = {
            "name" : dataset_name,
            "projectKey" : self.project_key,
            "type" : type,
            "params" : params,
            "formatType" : formatType,
            "formatParams" : formatParams
        }
        self.client._perform_json("POST", "/projects/%s/datasets/" % self.project_key,
                       body = obj)
        return DSSDataset(self.client, self.project_key, dataset_name)


    ########################################################
    # Managed folders
    ########################################################

    def list_managed_folders(self):
        """
        List the managed folders in this project
        
        Returns:
            the list of the managed folders, each one as a JSON object
        """
        return self.client._perform_json(
            "GET", "/projects/%s/managedfolders/" % self.project_key)

    def get_managed_folder(self, odb_id):
        """
        Get a handle to interact with a specific managed folder
       
        Args:
            odb_id: the identifier of the desired managed folder
        
        Returns:
            A :class:`dataikuapi.dss.managedfolder.DSSManagedFolder` managed folder handle
        """
        return DSSManagedFolder(self.client, self.project_key, odb_id)

    def create_managed_folder(self, name):
        """
        Create a new managed folder in the project, and return a handle to interact with it
        
        Args:
            name: the name of the managed folder
        
        Returns:
            A :class:`dataikuapi.dss.managedfolder.DSSManagedFolder` managed folder handle
        """
        obj = {
            "name" : name,
            "projectKey" : self.project_key
        }
        res = self.client._perform_json("POST", "/projects/%s/managedfolders/" % self.project_key,
                       body = obj)
        odb_id = res['id']
        return DSSManagedFolder(self.client, self.project_key, odb_id)


    ########################################################
    # Jobs
    ########################################################

    def list_jobs(self):
        """
        List the jobs in this project
        
        Returns:
            a list of the jobs, each one as a JSON object, containing both the definition and the state
        """
        return self.client._perform_json(
            "GET", "/projects/%s/jobs/" % self.project_key)

    def get_job(self, id):
        """
        Get a handler to interact with a specific job
        
        Returns:
            A :class:`dataikuapi.dss.job.DSSJob` job handle
        """
        return DSSJob(self.client, self.project_key, id)

    def start_job(self, definition):
        """
        Create a new job, and return a handle to interact with it
        
        Args:
            definition: the definition for the job to create. The definition must contain the type of job (RECURSIVE_BUILD, 
            NON_RECURSIVE_FORCED_BUILD, RECURSIVE_FORCED_BUILD, RECURSIVE_MISSING_ONLY_BUILD) and a list of outputs to build
        
        Returns:
            A :class:`dataikuapi.dss.job.DSSJob` job handle
        """
        job_def = self.client._perform_json("POST", "/projects/%s/jobs/" % self.project_key, body = definition)
        return DSSJob(self.client, self.project_key, job_def['id'])


    ########################################################
    # API Bundles
    ########################################################

    def list_api_services(self):
        """
        List the API services in this project
        
        Returns:
            the list of API services, each one as a JSON object
        """
        return self.client._perform_json(
            "GET", "/projects/%s/apiservices/" % self.project_key)

    def get_api_service(self, service_id):
        """
        Get a handle to interact with a specific API service
       
        Args:
            service_id: the ID of the desired API service
        
        Returns:
            A :class:`dataikuapi.dss.dataset.DSSAPIService` API Service handle
        """
        return DSSAPIService(self.client, self.project_key, service_id)


    ########################################################
    # Scenarios
    ########################################################

    def list_scenarios(self):
        """
        List the scenarios in this project
        
        Returns:
            the list of scenarios, each one as a JSON object.
        """
        return self.client._perform_json(
            "GET", "/projects/%s/scenarios/" % self.project_key)

    def get_scenario(self, scenario_id):
        """
        Get a handle to interact with a specific scenario
       
        Args:
            scenario_id: the ID of the desired scenario
        
        Returns:
            A :class:`dataikuapi.dss.dataset.DSSScenario` scenario handle
        """
        return DSSScenario(self.client, self.project_key, scenario_id)

