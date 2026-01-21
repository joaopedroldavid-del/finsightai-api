from fastapi import HTTPException, status


class AgentException( HTTPException ):

    def __init__( self, detail: str ):
        super().__init__( 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent error: {detail}"
         )


class ValidationException( HTTPException ):

    def __init__( self, detail: str ):
        super().__init__( 
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {detail}"
         )