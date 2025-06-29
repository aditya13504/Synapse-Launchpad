import asyncio
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
import uvicorn
from fastapi import FastAPI
import grpc
from grpc_reflection.v1alpha import reflection

from src.rest_api import create_rest_app
from src.grpc_server import FeatureStoreServicer, add_FeatureStoreServicer_to_server
from src.feature_store_pb2 import DESCRIPTOR
from src.pipeline import FeaturePipeline
from src.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureStoreServer:
    """
    Main server that runs both REST and gRPC services
    """
    
    def __init__(self):
        self.config = Config()
        self.pipeline = FeaturePipeline(self.config)
        self.grpc_server = None
        self.rest_app = None
        
    async def start_services(self):
        """Start all services"""
        try:
            # Initialize pipeline
            await self.pipeline.initialize()
            
            # Start gRPC server in background thread
            grpc_thread = threading.Thread(target=self.start_grpc_server, daemon=True)
            grpc_thread.start()
            
            # Create REST app
            self.rest_app = create_rest_app(self.pipeline)
            
            logger.info("Feature Store services started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start services: {e}")
            raise
    
    def start_grpc_server(self):
        """Start gRPC server"""
        try:
            self.grpc_server = grpc.server(ThreadPoolExecutor(max_workers=10))
            
            # Add servicer
            servicer = FeatureStoreServicer(self.pipeline)
            add_FeatureStoreServicer_to_server(servicer, self.grpc_server)
            
            # Enable reflection
            SERVICE_NAMES = (
                'feature_store.FeatureStore',
                reflection.SERVICE_NAME,
            )
            reflection.enable_server_reflection(SERVICE_NAMES, self.grpc_server)
            
            # Start server
            listen_addr = f'[::]:{self.config.grpc_port}'
            self.grpc_server.add_insecure_port(listen_addr)
            self.grpc_server.start()
            
            logger.info(f"gRPC server started on port {self.config.grpc_port}")
            
            # Keep server running
            self.grpc_server.wait_for_termination()
            
        except Exception as e:
            logger.error(f"gRPC server failed: {e}")
    
    async def stop_services(self):
        """Stop all services"""
        try:
            if self.grpc_server:
                self.grpc_server.stop(grace=5)
            
            await self.pipeline.close()
            
            logger.info("Feature Store services stopped")
            
        except Exception as e:
            logger.error(f"Error stopping services: {e}")

async def main():
    """Main entry point"""
    server = FeatureStoreServer()
    
    try:
        await server.start_services()
        
        # Start REST API
        config = uvicorn.Config(
            app=server.rest_app,
            host="0.0.0.0",
            port=server.config.rest_port,
            log_level="info"
        )
        
        rest_server = uvicorn.Server(config)
        await rest_server.serve()
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await server.stop_services()

if __name__ == "__main__":
    asyncio.run(main())