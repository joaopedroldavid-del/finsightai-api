from typing import Dict, List, Optional
from datetime import datetime
import logging

from app.models.schemas import ChatResponse, ConversationHistory, AgentStatus, AgentType
from app.agents.factory import AgentFactory
from app.repositories.conversation_repository import ConversationRepository
from app.core.exceptions import AgentException

logger = logging.getLogger( __name__ )

class AgentService:
    def __init__( 
            self,
            agent_factory: AgentFactory,
            conversation_repo: ConversationRepository
     ):
        self.agent_factory = agent_factory
        self.conversation_repo = conversation_repo
        self._agents: Dict[AgentType, object] = {}

    async def initialize_agents( self ) -> None:
        try:
            self._agents[AgentType.FINANCIAL_MANAGER] = await self.agent_factory.create_financial_manager()
            logger.info( "Financial Manager agent initialized successfully" )
        except Exception as e:
            logger.error( f"Failed to initialize agents: {str( e )}" )
            raise AgentException( f"Agent initialization failed: {str( e )}" )

    async def process_message( 
            self,
            message: str,
            agent_type: AgentType = AgentType.FINANCIAL_MANAGER,
            conversation_id: Optional[str] = None,
            context: Dict = None
     ) -> ChatResponse:
        try:
            if not conversation_id:
                conversation_id = await self.conversation_repo.create_conversation()

            agent = self._get_agent( agent_type )

            history = await self.conversation_repo.get_conversation_messages( conversation_id )

            agent_context = {
                "conversation_id": conversation_id,
                "history": history,
                "user_context": context or {},
                "timestamp": datetime.now().isoformat()
            }

            result = await agent.run( message, deps=agent_context )

            if hasattr( result.response, 'model_dump' ):
                response_data = result.data.model_dump()
                response_text = self._format_structured_response( response_data )
            else:
                response_text = str( result.response )

            await self.conversation_repo.add_message( 
                conversation_id=conversation_id,
                role="user",
                content=message
             )
            await self.conversation_repo.add_message( 
                conversation_id=conversation_id,
                role="assistant",
                content=response_text
             )

            return ChatResponse( 
                response=response_text,
                conversation_id=conversation_id,
                agent_type=agent_type,
                timestamp=datetime.now(),
                metadata={
                    "processing_time": getattr( result, 'processing_time', None ),
                    "structured_data": response_data if 'response_data' in locals() else None
                }
             )

        except Exception as e:
            logger.error( f"Agent processing failed: {str( e )}" )
            raise AgentException( f"Message processing failed: {str( e )}" )

    def _format_structured_response( self, response_data: dict ) -> str:
        try:
            lines = []

            if 'presentation' in response_data:
                lines.append( f"## {response_data['presentation']}" )
                lines.append( "" )

            if 'asset_symbol' in response_data:
                lines.append( f"**Asset**: {response_data['asset_symbol']}" )

            if 'analysis_period' in response_data:
                lines.append( f"**Analysis Period**: {response_data['analysis_period']}" )
            lines.append( "" )

            if 'price_snapshot' in response_data:
                price = response_data['price_snapshot']
                lines.append( "### 📊 Price Analysis" )
                lines.append( f"- **Current Price**: ${price.get( 'current_price', 'N/A' )}" )
                lines.append( f"- **Price Change**: {price.get( 'price_change_percentage', 'N/A' )}%" )
                lines.append( f"- **Trend**: {price.get( 'trend_direction', 'N/A' )}" )
                lines.append( f"- **Trading Range**: {price.get( 'price_range', 'N/A' )}" )
                lines.append( "" )

            if 'market_sentiment' in response_data:
                sentiment = response_data['market_sentiment']
                lines.append( "### 📰 Market Sentiment" )
                if sentiment.get( 'fear_greed_index' ):
                    lines.append( f"- **Fear & Greed Index**: {sentiment['fear_greed_index']}/100" )
                lines.append( f"- **Overall Sentiment**: {sentiment.get( 'sentiment_score', 'N/A' )}" )
                lines.append( "" )

            if 'key_insights' in response_data and response_data['key_insights']:
                lines.append( "### 💡 Key Insights" )
                for insight in response_data['key_insights']:
                    lines.append( f"- {insight}" )
                lines.append( "" )

            if 'top_news_headlines' in response_data and response_data['top_news_headlines']:
                lines.append( "### 🗞️ Top News Headlines" )
                for i, headline in enumerate( response_data['top_news_headlines'][:5], 1 ):
                    lines.append( f"{i}. {headline}" )
                lines.append( "" )

            return "\n".join( lines )

        except Exception as e:
            logger.error( f"Error formatting structured response: {str( e )}" )
            return str( response_data )

    async def get_conversation_history( self, conversation_id: str ) -> ConversationHistory:
        try:
            return await self.conversation_repo.get_conversation( conversation_id )
        except ValueError as e:
            raise AgentException( f"Conversation not found: {str( e )}" )
        except Exception as e:
            logger.error( f"Error retrieving conversation: {str( e )}" )
            raise AgentException( "Failed to retrieve conversation history" )

    async def get_agent_status( self ) -> List[AgentStatus]:
        statuses = []
        for agent_type, agent_instance in self._agents.items():
            statuses.append( 
                AgentStatus( 
                    agent_type=agent_type,
                    is_available=agent_instance is not None,
                    last_health_check=datetime.now(),
                    version="1.0.0"
                 )
             )
        return statuses

    def _get_agent( self, agent_type: AgentType ) -> object:
        agent = self._agents.get( agent_type )
        if not agent:
            raise AgentException( f"Agent type {agent_type} not available" )
        return agent

    async def process_message(
            self,
            message: str,
            agent_type: AgentType = AgentType.FINANCIAL_MANAGER,
            conversation_id: Optional[str] = None,
            context: Dict = None
    ) -> ChatResponse:
        """
        Process a message through the specified agent and return response
        """
        try:
            # Get or create conversation
            if not conversation_id:
                conversation_id = await self.conversation_repo.create_conversation()

            # Get the appropriate agent
            agent = self._get_agent(agent_type)

            # Get conversation history for context
            history = await self.conversation_repo.get_conversation_messages(conversation_id)

            # Prepare the message with context information
            enhanced_message = self._enhance_message_with_context(
                message=message,
                history=history,
                user_context=context or {},
                conversation_id=conversation_id
            )

            # Process with agent - without context parameter
            # Try different parameter patterns based on PydanticAI version
            result = await self._run_agent_with_tools(agent, enhanced_message)

            # Extract response text
            response_text = self._extract_response_text(result)

            # Store the interaction
            await self.conversation_repo.add_message(
                conversation_id=conversation_id,
                role="user",
                content=message
            )
            await self.conversation_repo.add_message(
                conversation_id=conversation_id,
                role="assistant",
                content=response_text
            )

            # Build response
            return ChatResponse(
                response=response_text,
                conversation_id=conversation_id,
                agent_type=agent_type,
                timestamp=datetime.now(),
                metadata={
                    "processing_time": getattr(result, 'processing_time', None),
                    "tool_used": self._check_if_tools_used(result)
                }
            )

        except Exception as e:
            logger.error(f"Agent processing failed: {str(e)}")
            raise AgentException(f"Message processing failed: {str(e)}")

    async def _run_agent_with_tools(self, agent, message: str):
        """
        Run the agent with tools, handling different PydanticAI versions
        """
        try:
            # Try running with just the message (most common pattern)
            return await agent.run(message)
        except TypeError as e:
            if "unexpected keyword argument" in str(e):
                # Try alternative parameter patterns
                try:
                    # Try with prompt parameter
                    return await agent.run(prompt=message)
                except TypeError:
                    try:
                        # Try with input parameter
                        return await agent.run(input=message)
                    except TypeError:
                        # Last resort - try without any parameters (shouldn't happen)
                        return await agent.run()
            else:
                # Re-raise if it's a different error
                raise

    def _enhance_message_with_context(
            self,
            message: str,
            history: List[Dict[str, any]],
            user_context: Dict[str, any],
            conversation_id: str
    ) -> str:
        """
        Enhance the message with context information since we can't pass context directly
        """
        # Build context string from history
        context_lines = []

        # Add conversation history if available
        if history:
            context_lines.append("Previous conversation:")
            for msg in history[-6:]:  # Last 6 messages for context
                role = "User" if msg["role"] == "user" else "Assistant"
                context_lines.append(f"{role}: {msg['content']}")
            context_lines.append("")

        # Add user context if provided
        if user_context:
            context_lines.append("User context:")
            for key, value in user_context.items():
                context_lines.append(f"- {key}: {value}")
            context_lines.append("")

        # Add current message
        context_lines.append(f"Current question: {message}")

        # Combine everything
        enhanced_message = "\n".join(context_lines)

        # If the enhanced message is too long, use a simpler approach
        if len(enhanced_message) > 4000:
            logger.warning("Enhanced message too long, using simplified version")
            enhanced_message = f"Conversation ID: {conversation_id}\n\nQuestion: {message}"
            if user_context:
                enhanced_message += f"\n\nUser context: {user_context}"

        return enhanced_message

    def _extract_response_text(self, result) -> str:
        """Extract text content from agent response"""
        try:
            # For PydanticAI responses with parts
            if hasattr(result, 'parts') and result.parts:
                text_parts = []
                for part in result.parts:
                    if hasattr(part, 'content'):
                        text_parts.append(part.content)
                    elif isinstance(part, str):
                        text_parts.append(part)
                return "\n".join(text_parts)

            # For direct string responses
            elif isinstance(result, str):
                return result

            # For ModelResponse objects
            elif hasattr(result, 'data'):
                return str(result.data)

            # For responses with text attribute
            elif hasattr(result, 'text'):
                return result.text

            # Fallback
            else:
                logger.warning(f"Unexpected response type: {type(result)}")
                return str(result)

        except Exception as e:
            logger.error(f"Error extracting response text: {str(e)}")
            return str(result)

    def _check_if_tools_used(self, result) -> bool:
        """Check if the agent used any tools"""
        try:
            if hasattr(result, 'parts'):
                for part in result.parts:
                    if hasattr(part, 'tool_name'):
                        return True
                    if hasattr(part, 'tool_calls'):
                        return True
            return False
        except:
            return False